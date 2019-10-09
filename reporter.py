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

    @staticmethod
    def toomany(string: str) -> str:
        return '\033[95m' + string + '\033[0m'


def url_subst(url: str, item: str) -> str:
    return url.format(quote(item))


class Reporter:
    _project: str
    _entity: str
    _prefix: str = ''

    _verbose: bool = False

    _printed_header = False

    _html: List[str]

    def __init__(self, project: str, entity: str, verbose: bool = False) -> None:
        self._project = project
        self._entity = entity
        self._verbose = verbose

        self._html = []

    def set_prefix(self, prefix: str) -> None:
        self._prefix = prefix

    def _print_header(self) -> None:
        if not self._printed_header:
            project_str = self._project
            entity_str = self._entity
            if self._verbose:
                project_str += ' ({})'.format(Colors.url(url_subst('https://repology.org/project/{}', self._project)))
                entity_str += ' ({})'.format(Colors.url(url_subst('https://wikidata.org/wiki/{}', self._entity)))

            print('===> {} / {}'.format(project_str, entity_str), file=sys.stderr)
            self._printed_header = True

    def _print_action(self, message: str) -> None:
        print(self._prefix + message, file=sys.stderr)

    def _print_html(self, html: str, cls: str) -> None:
        self._html.append('<td class="table-{}">{}{}</td>'.format(cls, self._prefix, html))

    def _item_url(self, value: str, url: str) -> str:
        if self._verbose:
            return value + ' (' + url + ')'
        else:
            return value

    def action_add(self, value: str, url: str) -> None:
        self._print_header()

        url = url_subst(url, value)

        self._print_action('adding ' + self._item_url(Colors.action(value), Colors.url(url)))
        self._print_html('adding <a href="{}">{}</a>'.format(url, value), 'success')

    def action_novalue(self) -> None:
        self._print_header()
        self._print_action(Colors.manual('no value') + ' encountered, please remove')
        self._print_html('<b>no value</b> encountered, please remove', 'warning')

    def action_remove(self, value: str, url: str, histurls: List[str]) -> None:
        self._print_header()

        url = url_subst(url, value)

        self._print_action(
            '{} not present in Repology, needs investigation; see following urls:\n  {}'.format(
                self._item_url(Colors.manual(value), Colors.url(url)),
                '\n  '.join(Colors.url(url_subst(url, value)) for url in histurls)
            )
        )
        self._print_html(
            '<a href="{}">{}</a> not present in Repology, needs investigation; see following urls: {}'.format(
                url,
                value,
                ' '.join('<a href="{}">[{}]</a>'.format(url_subst(url, value), n) for n, url in enumerate(histurls, 1))
            ),
            'danger'
        )

    def action_toomany(self, count: int) -> None:
        self._print_header()

        self._print_action(Colors.toomany('too many ({}) packages in Repology, skipping'.format(count)))
        self._print_html('too many ({}) packages in Repology, skipping'.format(count), 'warning')

    def action_fallback(self) -> None:
        if not self._printed_header:
            self._print_header()
            print(Colors.noaction('no action needed'), file=sys.stderr)

    def dump_html(self) -> str:
        if not self._html:
            return ''

        html = '<tr>'
        html += '<td rowspan="{}"><a href="{}">{}</a></td>'.format(len(self._html), url_subst('https://repology.org/project/{}#wikidata', self._project), self._project)
        html += '<td rowspan="{}"><a href="{}">{}</a></td>'.format(len(self._html), url_subst('https://wikidata.org/wiki/{}', self._entity), self._entity)
        html += '{}'.format(self._html[0])
        html += '</tr>'

        html += ''.join('<tr>{}</tr>'.format(item) for item in self._html[1:])

        return html

    @staticmethod
    def html_header() -> str:
        return """
            <html>
                <head>
                    <title>Repology wikidata bot report</title>
                    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
                </head>
                <body>
                    <div class="container">
                        <h1>Repology wikidata bot report</h1>
                        <table class="table table-sm table-hover">
                            <thead>
                                <tr><th>Repology project</th><th>Wikidata entity</th><th>Action</th></tr>
                            </thead>
                            <tbody>
            """

    @staticmethod
    def html_footer() -> str:
        return '</tbody></table></div></body></html>'
