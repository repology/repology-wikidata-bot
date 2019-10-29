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

from typing import Iterable

from jinja2 import Template

from reports import ReportItem


def format_html_report(items: Iterable[ReportItem]) -> str:
    return Template("""
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
                            <tr><th>Wikidata item</th><th>Repology project(s)</th><th>Action</th></tr>
                        </thead>
                        <tbody>
                        {% for item in items %}
                            <tr>
                                <td rowspan="{{ item.actions|length }}"><a href="https://wikidata.org/wiki/{{ item.item }}">{{ item.item }}</a></td>
                                <td rowspan="{{ item.actions|length }}">
                                {% for projectname in item.projectnames %}
                                    <a href="https://repology.org/project/{{ projectname }}#wikidata">{{ projectname }}</a>
                                {% endfor %}
                                </td>
                                {% for action in item.actions %}
                            {% if not loop.first %}</tr><tr>{% endif %}
                                {% if action.__class__.__name__ == 'AddPropertyAction' %}
                                    <td class="table-success">{{ action.repo }} ({{ action.prop }}): adding <a href="{{ action.url }}">{{ action.value }}</a></td>
                                {% elif action.__class__.__name__ == 'RemovePropertyAction' %}
                                    <td class="table-danger">{{ action.repo }} ({{ action.prop }}):
                                        <a href="{{ action.url }}">{{ action.value }}</a> not present in Repology, needs investigation; see following urls:
                                        {% for histurl in action.histurls %}
                                            <a href="{{ histurl }}">[{{ loop.index }}]</a>
                                        {% endfor %}
                                    </td>
                                {% elif action.__class__.__name__ == 'NoValueAction' %}
                                    <td class="table-warning">{{ action.repo }} ({{ action.prop }}): <b>no value</b> encountered, please remove</td>
                                {% elif action.__class__.__name__ == 'TooManyValuesAction' %}
                                    <td class="table-warning">{{ action.repo }} ({{ action.prop }}): too many ({{ action.count }}) packages in Repology, skipping</td>
                                {% elif action.__class__.__name__ == 'MultipleItemsAction' %}
                                    <td class="table-danger">multiple wikidata items for project, skipping</td>
                                {% else %}
                                    <td class="table-danger">unknown action</td>
                                {% endif %}
                                {% endfor %}
                            </tr>
                        {% endfor %}
                        </tbody>
                    </table>
                </div>
            </body>
        </html>
    """).render(items=items)
