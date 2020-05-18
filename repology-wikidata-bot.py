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
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Set

from actions import Action, ActionPerformer, AddPropertyAction, MultipleItemsAction, NoValueAction, RemovePropertyAction, TooManyValuesAction

from apis.repology import RepologyProject, iterate_repology_projects
from apis.wikidata import WikidataApi

from reports import aggregate_report
from reports.html import format_html_report
from reports.text import format_text_report

from utils.progress import progressify


@dataclass
class RepologyWikidataMapping:
    repo: str
    prop: str
    field: str
    url: str
    histurls: List[str]
    ignore_missing: bool = False


PACKAGE_MAPPINGS = [
    RepologyWikidataMapping(
        repo='gentoo',
        prop='P3499',
        field='srcname',
        url='https://packages.gentoo.org/packages/{}',
        histurls=[
            'https://gitweb.gentoo.org/repo/gentoo.git/log/{}'
        ],
    ),
    RepologyWikidataMapping(
        repo='arch',
        prop='P3454',
        field='binname',
        url='https://www.archlinux.org/packages/?q={}',
        histurls=[
            'https://git.archlinux.org/svntogit/packages.git/log/trunk?h=packages/{}',
            'https://git.archlinux.org/svntogit/community.git/log/trunk?h=packages/{}',
        ],
    ),
    RepologyWikidataMapping(
        repo='aur',
        prop='P4162',
        field='binname',
        url='https://aur.archlinux.org/packages/{}/',
        histurls=[
            'https://aur.archlinux.org/cgit/aur.git/log/?h={}'
        ],
        # it seems like packages disappear from AUR index when they are moved
        # to primary Arch repos, but they still remain in AUR VCS; let's just
        # skip these
        ignore_missing=True,
    ),
    RepologyWikidataMapping(
        repo='freebsd',
        prop='P7427',
        field='srcname',
        url='https://www.freshports.org/{}',
        histurls=[
            'https://www.freshports.org/{}'
        ],
    ),
    RepologyWikidataMapping(
        repo='libregamewiki',
        prop='P6666',
        field='name',
        url='https://libregamewiki.org/{}',
        histurls=[
            'https://libregamewiki.org/{}'
        ],
        # Repology data on LGW is incomplete (investigating), so silence missing
        # entries as well
        ignore_missing=True,
    ),
    RepologyWikidataMapping(
        repo='crates_io',
        prop='P4763',
        field='name',
        url='https://crates.io/crates/{}',
        histurls=[
            'https://crates.io/crates/{}'
        ],
    ),
    RepologyWikidataMapping(
        repo='rubygems',
        prop='P5566',
        field='name',
        url='https://rubygems.org/gems/{}',
        histurls=[
            'https://rubygems.org/gems/{}'
        ],
    ),
    RepologyWikidataMapping(
        repo='cran',
        prop='P5565',
        field='name',
        url='https://cran.r-project.org/web/packages/{}/index.html',
        histurls=[
            'https://cran.r-project.org/web/packages/{}/index.html',
        ],
    ),
    RepologyWikidataMapping(
        repo='gnu_elpa',
        prop='P6823',
        field='name',
        url='https://elpa.gnu.org/packages/{}.html',
        histurls=[
            'https://elpa.gnu.org/packages/{}.html',
        ],
    ),
    RepologyWikidataMapping(
        repo='melpa',
        prop='P6888',
        field='name',
        url='http://melpa.org/#/{}',
        histurls=[
            'http://melpa.org/#/{}',
        ],
    ),
    RepologyWikidataMapping(
        repo='pkgsrc_current',
        prop='P7966',
        field='srcname',
        url='https://pkgsrc.se/{}',
        histurls=[
            'https://pkgsrc.se/{}'
        ],
    ),
    RepologyWikidataMapping(
        repo='openbsd',
        prop='P7967',
        field='srcname',
        url='http://openports.se/{}',
        histurls=[
            'http://openports.se/{}',
            'https://cvsweb.openbsd.org/ports/{}'
        ],
    ),
    # Does not provide link to a single package
    # RepologyWikidataMapping(
    #    repo='gnuguix',
    #    prop='P6765',
    #    field='name',
    #    url='-',
    #    histurls=[
    #    ],
    # ),
    # Not yet: need different kind of name (Template::Toolkit, not Template-Toolkit)
    # RepologyWikidataMapping(
    #    repo='metacpan',
    #    prop='P5779',
    #    field='name',
    #    url='https://metacpan.org/pod/{}',
    #    histurls=[
    #        'https://metacpan.org/pod/{}',
    #    ],
    # ),
]


def construct_blacklist(options: argparse.Namespace) -> Set[str]:
    blacklist: Set[str] = set()

    if options.blacklist:
        with open(options.blacklist, 'r') as blacklist_fd:
            for line in blacklist_fd:
                item = line.split('#', 1)[0].strip()

                if item:
                    blacklist.add(item)

    if options.exclude:
        blacklist.update(options.exclude)

    return blacklist


ProjectsByItem = Dict[str, List[RepologyProject]]


def gather_repology_projects(options: argparse.Namespace) -> ProjectsByItem:
    blacklist = construct_blacklist(options)

    projects_by_item: ProjectsByItem = defaultdict(list)

    repology_iter = iterate_repology_projects(apiurl=options.repology_api, begin_name=options.from_, end_name=options.to)

    for project in progressify(repology_iter, 'Gathering projects from Repology'):
        if project.name not in blacklist:
            for item in project.values_by_repo_field.get(('wikidata', 'name'), []):
                if item not in blacklist:
                    projects_by_item[item].append(project)

    return projects_by_item


def run(options: argparse.Namespace) -> None:
    projects_by_item = gather_repology_projects(options)

    wikidata = WikidataApi()

    actions: List[Action] = []

    for item, projects in progressify(projects_by_item.items(), 'Comparing to Wikidata'):
        projectnames = list(project.name for project in projects)

        wikidata_items: Set[str] = set()

        for project in projects:
            wikidata_items.update(project.values_by_repo_field.get(('wikidata', 'name'), []))

        if len(wikidata_items) > 1:
            actions.append(MultipleItemsAction(item=item, projectnames=projectnames))
            continue

        for mapping in PACKAGE_MAPPINGS:
            if options.repositories and mapping.repo not in options.repositories and mapping.prop not in options.repositories:
                continue

            repology_values: Set[str] = set()

            for project in projects:
                repology_values.update(project.values_by_repo_field.get((mapping.repo, mapping.field), []))

            wikidata_values = set(wikidata.iter_claims(item, mapping.prop))
            wikidata_all_values = set(wikidata.iter_claims(item, mapping.prop, allow_deprecated=True))

            missing = repology_values - wikidata_all_values
            extra = wikidata_values - repology_values

            if missing and len(repology_values) > options.max_entries:
                actions.append(
                    TooManyValuesAction(
                        item=item,
                        projectnames=projectnames,
                        repo=mapping.repo,
                        prop=mapping.prop,
                        count=len(repology_values)
                    )
                )
            else:
                for mvalue in missing:
                    actions.append(
                        AddPropertyAction(
                            item=item,
                            projectnames=projectnames,
                            repo=mapping.repo,
                            prop=mapping.prop,
                            value=mvalue,
                            url=mapping.url.format(mvalue)
                        )
                    )

                for evalue in extra:
                    if evalue is None:
                        actions.append(
                            NoValueAction(
                                item=item,
                                projectnames=projectnames,
                                repo=mapping.repo,
                                prop=mapping.prop,
                            )
                        )
                    elif not mapping.ignore_missing:
                        actions.append(
                            RemovePropertyAction(
                                item=item,
                                projectnames=projectnames,
                                repo=mapping.repo,
                                prop=mapping.prop,
                                value=evalue,
                                url=mapping.url.format(evalue),
                                histurls=[url.format(evalue) for url in mapping.histurls]
                            )
                        )

    print('Listing actions', file=sys.stderr)
    report = list(aggregate_report(actions))
    format_text_report(report, options.verbose)

    if options.html:
        with open(options.html, 'w') as html:
            html.write(format_html_report(report))

    if options.dry_run:
        return

    if not options.yes:
        while True:
            key = input('Apply listed changes [Y/n]? ')
            if key in ['', 'y', 'Y']:
                break
            if key in ['n', 'N']:
                return

    performer = ActionPerformer(wikidata)

    actions = [action for action in actions if performer.is_performable(action)]
    for action in progressify(actions, 'Applying actions'):
        performer.perform(action)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--repology-api', metavar='URL', default='https://repology.org/api/v1/projects/', help='URL of Repology projects API endpoint (must end with slash)')
    parser.add_argument('--from', metavar='NAME', help='minimal project name to operate on', dest='from_')
    parser.add_argument('--to', metavar='NAME', help='maximal project name to operate on')
    parser.add_argument('--exclude', metavar='NAME', nargs='*', help='exclude specified project names or wikidata items from processing')
    parser.add_argument('--blacklist', default='blacklist.txt', help='path to blacklist with additional excludes')
    parser.add_argument('-n', '--dry-run', action='store_true', help='perform a trial run with no changes made')
    parser.add_argument('-y', '--yes', action='store_true', help='assume yes')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
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
