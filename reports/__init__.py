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

from collections import defaultdict
from dataclasses import astuple, dataclass
from typing import Dict, Iterable, List, Tuple

from actions import Action


@dataclass
class ReportItem:
    item: str
    projectnames: List[str]
    actions: List[Action]


def aggregate_report(actions: Iterable[Action]) -> Iterable[ReportItem]:
    by_item: Dict[Tuple[str, ...], List[Action]] = defaultdict(list)

    for action in actions:
        by_item[tuple([action.item] + action.projectnames)].append(action)

    for key, actions in sorted(by_item.items()):
        if actions:
            yield ReportItem(key[0], list(key[1:]), sorted(actions, key=astuple))
