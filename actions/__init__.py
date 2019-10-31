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

from dataclasses import dataclass
from typing import List

from apis.wikidata import WikidataApi


@dataclass
class Action:
    item: str
    projectnames: List[str]


@dataclass
class AddPropertyAction(Action):
    repo: str
    prop: str
    value: str
    url: str


@dataclass
class RemovePropertyAction(Action):
    repo: str
    prop: str
    value: str
    url: str
    histurls: List[str]


@dataclass
class NoValueAction(Action):
    repo: str
    prop: str


@dataclass
class TooManyValuesAction(Action):
    repo: str
    prop: str
    count: int


@dataclass
class MultipleItemsAction(Action):
    pass


class ActionPerformer:
    wikidata: WikidataApi

    def __init__(self, wikidata: WikidataApi) -> None:
        self.wikidata = wikidata

    def perform(self, action: Action) -> None:
        if isinstance(action, AddPropertyAction):
            self.wikidata.add_claim(action.item, action.prop, action.value, 'adding package information from Repology')
