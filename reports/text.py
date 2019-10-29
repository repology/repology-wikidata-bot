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
from typing import Iterable
from urllib.parse import quote

from actions import AddPropertyAction, MultipleItemsAction, NoValueAction, RemovePropertyAction, TooManyValuesAction

from reports import ReportItem


class _Colors:
    @staticmethod
    def url(string: str) -> str:
        return '\033[94m' + string + '\033[0m'

    @staticmethod
    def add(string: str) -> str:
        return '\033[92m' + string + '\033[0m'

    @staticmethod
    def remove(string: str) -> str:
        return '\033[91m' + string + '\033[0m'

    @staticmethod
    def skipped(string: str) -> str:
        return '\033[95m' + string + '\033[0m'


def _url_subst(url: str, item: str) -> str:
    return url.format(quote(item))


def format_text_report(items: Iterable[ReportItem], verbose: bool = False) -> None:
    def item_url(value: str, url: str) -> str:
        if verbose:
            return value + ' (' + url + ')'
        else:
            return value

    for item in items:
        print(
            '===> {} / {}'.format(
                item_url(item.item, _Colors.url(_url_subst('https://wikidata.org/wiki/{}', item.item))),
                ','.join(
                    item_url(projectname, _Colors.url(_url_subst('https://repology.org/project/{}', projectname)))
                    for projectname in item.projectnames
                )
            ),
            file=sys.stderr
        )

        for action in item.actions:
            def print_item(text: str) -> None:
                if hasattr(action, 'repo') and hasattr(action, 'prop'):
                    prefix = f'{action.repo} ({action.prop}): '  # type: ignore
                else:
                    prefix = ''

                print(prefix + text, file=sys.stderr)

            if isinstance(action, AddPropertyAction):
                itemstr = item_url(_Colors.add(action.value), _Colors.url(action.url))
                print_item('adding ' + itemstr)
            elif isinstance(action, RemovePropertyAction):
                itemstr = item_url(_Colors.remove(action.value), _Colors.url(action.url))
                urls = '\n'.join('  ' + _Colors.url(url) for url in action.histurls)
                print_item(itemstr + ' not present in Repology, needs investigation; see following urls:\n' + urls)
            elif isinstance(action, NoValueAction):
                print_item(_Colors.remove('no value') + ' encountered, please remove')
            elif isinstance(action, TooManyValuesAction):
                print_item(_Colors.skipped('too many ({}) packages in Repology, skipping'.format(action.count)))
            elif isinstance(action, MultipleItemsAction):
                print_item(_Colors.skipped('multiple wikidata items for project, skipping'))
            else:
                assert(False)
