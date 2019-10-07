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

import sys
from typing import List
from urllib.parse import quote


class Colors:
    @staticmethod
    def action(string: str) -> str:
        return '\033[92m' + string + '\033[0m'

    @staticmethod
    def manual(string: str) -> str:
        return '\033[93m' + string + '\033[0m'

    @staticmethod
    def url(string: str) -> str:
        return '\033[94m' + string + '\033[0m'

    @staticmethod
    def noaction(string: str) -> str:
        return '\033[94m' + string + '\033[0m'


def url_subst(url: str, item: str) -> str:
    return Colors.url(url.format(quote(item)))


class Reporter:
    _project: str
    _entity: str
    _prefix: str = ''

    _verbose: bool = False

    _printed_header = False

    def __init__(self, project: str, entity: str, verbose: bool = False) -> None:
        self._project = project
        self._entity = entity
        self._verbose = verbose

    def set_prefix(self, prefix: str) -> None:
        self._prefix = prefix

    def _print_header(self) -> None:
        if not self._printed_header:
            project_str = self._project
            entity_str = self._entity
            if self._verbose:
                project_str += ' ({})'.format(url_subst('https://repology.org/project/{}', self._project))
                entity_str += ' ({})'.format(url_subst('https://wikidata.org/wiki/{}', self._entity))

            print('===> {} / {}'.format(project_str, entity_str), file=sys.stderr)
            self._printed_header = True

    def action_add(self, value: str, url: str) -> None:
        self._print_header()

        item_str = Colors.action(value)
        if self._verbose:
            item_str += ' ({})'.format(url_subst(url, value))

        print('{}adding {}'.format(self._prefix, item_str), file=sys.stderr)

    def action_novalue(self) -> None:
        self._print_header()

        print('{}{} encountered, please remove'.format(self._prefix, Colors.manual('no value')), file=sys.stderr)

    def action_remove(self, value: str, urls: List[str]) -> None:
        self._print_header()

        print('{}{} not present in Repology, needs investigation; see following urls:'.format(self._prefix, Colors.manual(value)), file=sys.stderr)
        for url in urls:
            print('  {}'.format(Colors.manual(url_subst(url, value))), file=sys.stderr)

    def action_fallback(self) -> None:
        if not self._printed_header:
            self._print_header()
            print(Colors.noaction('no action needed'), file=sys.stderr)
