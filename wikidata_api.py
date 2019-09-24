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

from typing import Any, List, Optional

import pywikibot


class WikidataApi:
    _site: Any
    _repo: Any

    def __init__(self) -> None:
        self._site = pywikibot.Site('wikidata', 'wikidata')
        self._repo = self._site.data_repository()

    def get_claims(self, entry: str, prop: str, allow_deprecated: bool = False) -> List[Optional[str]]:
        item = pywikibot.ItemPage(self._repo, entry)
        item_dict = item.get()
        claims = item_dict['claims']

        if prop not in claims:
            return []

        return [claim.getTarget() for claim in claims[prop] if allow_deprecated or claim.getRank() != 'deprecated']

    def add_claim(self, entry: str, prop: str, value: str, summary: str) -> None:
        item = pywikibot.ItemPage(self._repo, entry)

        claim = pywikibot.Claim(self._repo, prop)
        claim.setTarget(value)

        item.addClaim(claim, summary=summary)
