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

from repology_api import iterate_repology_projects

from wikidata_api import WikidataApi


REPO_TO_PROPERTY = {
    'gentoo': 'P3499',
}


class Colors:
    ACTION = '\033[92m'
    MANUAL = '\033[93m'
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


def run(options: argparse.Namespace) -> None:
    wikidata = WikidataApi()

    for project in iterate_repology_projects(apiurl=options.repology_api, begin_name=getattr(options, 'from'), end_name=options.to):
        wikidata_entries = project.package_names_by_repo.get('wikidata')

        if wikidata_entries is None:
            # not present in wikidata
            continue

        for entry in wikidata_entries:
            ar = ActionReporter(project.name, entry)

            for repo, prop in REPO_TO_PROPERTY.items():
                repology_values = set(project.package_names_by_repo.get(repo, []))
                wikidata_values = set(wikidata.get_claims(entry, prop))
                wikidata_all_values = set(wikidata.get_claims(entry, prop, allow_deprecated=True))

                missing = repology_values - wikidata_all_values
                extra = wikidata_values - repology_values

                for item in missing:
                    ar.report('{} ({}): adding {}'.format(repo, prop, Colors.ACTION + item + Colors.ENDC))

                    if not options.dry_run:
                        wikidata.add_claim(entry, prop, item, 'adding package information from Repology')

                for item in extra:
                    ar.report('{} ({}): {} not present in Repology, needs investigation'.format(repo, prop, Colors.MANUAL + item + Colors.ENDC))


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--repology-api', metavar='URL', default='https://repology.org/api/v1/projects/', help='URL of Repology projects API endpoint (must end with slash)')
    parser.add_argument('--from', metavar='NAME', help='minimal project name to operate on')
    parser.add_argument('--to', metavar='NAME', help='maximal project name to operate on')
    parser.add_argument('-n', '--dry-run', action='store_true', help='perform a trial run with no changes made')

    return parser.parse_args()


def main() -> int:
    options = parse_arguments()

    run(options)

    return 0


if __name__ == '__main__':
    sys.exit(main())
