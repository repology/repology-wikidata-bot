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

from repology_api import iterate_repology_projects

from wikidata_api import WikidataApi


@dataclass
class RepologyWikidataMapping:
    repo: str
    prop: str
    field: str


PACKAGE_MAPPINGS = [
    RepologyWikidataMapping(repo='gentoo', prop='P3499', field='keyname'),
    RepologyWikidataMapping(repo='arch', prop='P3454', field='name'),
    RepologyWikidataMapping(repo='aur', prop='P4162', field='name'),
]


class Colors:
    ACTION = '\033[92m'
    MANUAL = '\033[93m'
    NOACTION = '\033[94m'
    ENDC = '\033[0m'


class ActionReporter:
    _repology_project: str
    _wikidata_entry: str
    _header_shown: bool

    def __init__(self, repology_project: str, wikidata_entry: str) -> None:
        self._repology_project = repology_project
        self._wikidata_entry = wikidata_entry
        self._header_shown = False

    def report(self, message: str) -> None:
        if not self._header_shown:
            print('===> {} ({})'.format(self._repology_project, self._wikidata_entry), file=sys.stderr)
            self._header_shown = True

        print(message, file=sys.stderr)

    def mention(self, message: str = Colors.NOACTION + 'no action needed' + Colors.ENDC) -> None:
        if not self._header_shown:
            self.report(message)


def run(options: argparse.Namespace) -> None:
    wikidata = WikidataApi()

    for project in iterate_repology_projects(apiurl=options.repology_api, begin_name=options.from_, end_name=options.to):
        wikidata_entries = project.values_by_repo_field.get(('wikidata', 'keyname'))

        if wikidata_entries is None:
            # not present in wikidata
            continue

        for entry in wikidata_entries:
            ar = ActionReporter(project.name, entry)

            for mapping in PACKAGE_MAPPINGS:
                repology_values = project.values_by_repo_field.get((mapping.repo, mapping.field), set())
                wikidata_values = set(wikidata.get_claims(entry, mapping.prop))
                wikidata_all_values = set(wikidata.get_claims(entry, mapping.prop, allow_deprecated=True))

                missing = repology_values - wikidata_all_values
                extra = wikidata_values - repology_values

                for mitem in missing:
                    ar.report('Packages/{} ({}): adding {}'.format(mapping.repo, mapping.prop, Colors.ACTION + mitem + Colors.ENDC))

                    if not options.dry_run:
                        wikidata.add_claim(entry, mapping.prop, mitem, 'adding package information from Repology')

                for eitem in extra:
                    if eitem is None:
                        ar.report('Packages/{} ({}): "{}no value{}" encountered, should be fixed'.format(mapping.repo, mapping.prop, Colors.MANUAL, Colors.ENDC))
                    else:
                        ar.report('Packages/{} ({}): {} not present in Repology, needs investigation'.format(mapping.repo, mapping.prop, Colors.MANUAL + eitem + Colors.ENDC))

            if options.verbose:
                ar.mention()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--repology-api', metavar='URL', default='https://repology.org/api/v1/projects/', help='URL of Repology projects API endpoint (must end with slash)')
    parser.add_argument('--from', metavar='NAME', help='minimal project name to operate on', dest='from_')
    parser.add_argument('--to', metavar='NAME', help='maximal project name to operate on')
    parser.add_argument('-n', '--dry-run', action='store_true', help='perform a trial run with no changes made')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')

    return parser.parse_args()


def main() -> int:
    options = parse_arguments()

    run(options)

    return 0


if __name__ == '__main__':
    sys.exit(main())
