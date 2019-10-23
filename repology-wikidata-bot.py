#!/usr/bin/env python3
#
# Copyright (C) 2019 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of repology-wikidata-bot
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import sys
from dataclasses import dataclass
from typing import IO, Iterable, List, Optional, Set

from repology_api import iterate_repology_projects

from reporter import Reporter

from wikidata_api import WikidataApi


@dataclass
class RepologyWikidataMapping:
    repo: str
    prop: str
    field: str
    url: str
    histurls: List[str]


PACKAGE_MAPPINGS = [
    RepologyWikidataMapping(
        repo='gentoo',
        prop='P3499',
        field='keyname',
        url='https://packages.gentoo.org/packages/{}',
        histurls=[
            'https://gitweb.gentoo.org/repo/gentoo.git/log/{}'
        ],
    ),
    RepologyWikidataMapping(
        repo='arch',
        prop='P3454',
        field='name',
        url='https://www.archlinux.org/packages/?q={}',
        histurls=[
            'https://git.archlinux.org/svntogit/packages.git/log/trunk?h=packages/{}',
            'https://git.archlinux.org/svntogit/community.git/log/trunk?h=packages/{}',
        ],
    ),
    RepologyWikidataMapping(
        repo='aur',
        prop='P4162',
        field='name',
        url='https://aur.archlinux.org/packages/{}/',
        histurls=[
            'https://aur.archlinux.org/cgit/aur.git/log/?h={}'
        ],
    ),
    RepologyWikidataMapping(
        repo='freebsd',
        prop='P7427',
        field='keyname',
        url='https://www.freshports.org/{}',
        histurls=[
           'https://www.freshports.org/{}'
        ],
    ),
]


def read_blacklist(path: str) -> Iterable[str]:
    with open(path, 'r') as blacklist:
        for line in blacklist:
            item = line.split('#', 1)[0].strip()

            if item:
                yield item


def run(options: argparse.Namespace) -> None:
    blacklist: Set[str] = set()

    if options.blacklist:
        blacklist.update(read_blacklist(options.blacklist))

    if options.exclude:
        blacklist.update(options.exclude)

    wikidata = WikidataApi()

    html: Optional[IO[str]] = None

    if options.html:
        html = open(options.html, 'w')
        html.write(Reporter.html_header())
        html.flush()

    for project in iterate_repology_projects(apiurl=options.repology_api, begin_name=options.from_, end_name=options.to):
        if project.name in blacklist:
            continue

        wikidata_entries = project.values_by_repo_field.get(('wikidata', 'keyname'))

        if wikidata_entries is None:
            # not present in wikidata
            continue

        for entry in wikidata_entries:
            reporter = Reporter(project.name, entry, verbose=options.verbose >= 1)

            for mapping in PACKAGE_MAPPINGS:
                if options.repositories and mapping.repo not in options.repositories and mapping.prop not in options.repositories:
                    continue

                repology_values = project.values_by_repo_field.get((mapping.repo, mapping.field), set())
                wikidata_values = set(wikidata.get_claims(entry, mapping.prop))
                wikidata_all_values = set(wikidata.get_claims(entry, mapping.prop, allow_deprecated=True))

                missing = repology_values - wikidata_all_values
                extra = wikidata_values - repology_values

                reporter.set_prefix('{} ({}): '.format(mapping.repo, mapping.prop))

                if missing and len(repology_values) > options.max_entries:
                    reporter.action_toomany(len(repology_values))
                else:
                    for mitem in missing:
                        reporter.action_add(mitem, mapping.url)

                        if not options.dry_run:
                            wikidata.add_claim(entry, mapping.prop, mitem, 'adding package information from Repology')

                for eitem in extra:
                    if eitem is None:
                        reporter.action_novalue()
                    else:
                        reporter.action_remove(eitem, mapping.url, mapping.histurls)

            if options.verbose >= 2:
                reporter.action_fallback()

            if html:
                html.write(reporter.dump_html())
                html.flush()

    if html:
        html.write(Reporter.html_footer())
        html.flush()
        html.close()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--repology-api', metavar='URL', default='https://repology.org/api/v1/projects/', help='URL of Repology projects API endpoint (must end with slash)')
    parser.add_argument('--from', metavar='NAME', help='minimal project name to operate on', dest='from_')
    parser.add_argument('--to', metavar='NAME', help='maximal project name to operate on')
    parser.add_argument('--exclude', metavar='NAME', nargs='*', help='exclude specified project names from processing')
    parser.add_argument('--blacklist', default='blacklist.txt', help='path to blacklist with additional excludes')
    parser.add_argument('-n', '--dry-run', action='store_true', help='perform a trial run with no changes made')
    parser.add_argument('-v', '--verbose', default=0, action='count', help='verbose mode (may specify twice)')
    parser.add_argument('--repositories', nargs='*', help='limit operation to specifiad list of repositories (may use either repology names or wikidata properties)')
    parser.add_argument('--html', metavar='PATH', help='enable HTML output, specifying path to it')
    parser.add_argument('--max-entries', default=50, help='skip projects with more packages than this')

    return parser.parse_args()


def main() -> int:
    options = parse_arguments()

    run(options)

    return 0


if __name__ == '__main__':
    sys.exit(main())
