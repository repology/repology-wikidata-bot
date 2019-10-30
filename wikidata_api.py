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

from typing import Any, Iterable, Optional, Tuple

import pywikibot


class WikidataApi:
    _site: Any
    _repo: Any
    _cache_item: str
    _cache_page: Any

    def __init__(self) -> None:
        self._site = pywikibot.Site('wikidata', 'wikidata')
        self._repo = self._site.data_repository()
        self._cache_item = ''
        self._cache_item = None

    def _get_page(self, item: str) -> Any:
        if self._cache_item != item:
            self._cache_item = item
            self._cache_page = pywikibot.ItemPage(self._repo, item)

        return self._cache_page

    def iter_claims(self, item: str, prop: str, allow_deprecated: bool = False) -> Iterable[Optional[str]]:
        page = self._get_page(item)

        page_dict = page.get()
        claims = page_dict['claims']

        if prop not in claims:
            return

        for claim in claims[prop]:
            deprecated = claim.getRank() == 'deprecated'
            expired = 'P582' in claim.qualifiers

            if allow_deprecated or not (deprecated or expired):
                yield claim.getTarget()

    def add_claim(self, item: str, prop: str, value: str, summary: str) -> None:
        page = pywikibot.ItemPage(self._repo, item)

        claim = pywikibot.Claim(self._repo, prop)
        claim.setTarget(value)

        page.addClaim(claim, summary=summary)
