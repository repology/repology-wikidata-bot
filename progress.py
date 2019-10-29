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
from typing import Any, Iterable


def progressify(iterable: Any, message: str) -> Iterable[Any]:
    print('{}...'.format(message), end='\r', file=sys.stderr)

    count = len(iterable) if hasattr(iterable, '__len__') else None

    def print_progress(num: int, end: str) -> None:
        if count is None:
            print('{} [{}]...'.format(message, num), end=end, file=sys.stderr)
        else:
            print('{} [{}/{}]...'.format(message, num, count), end=end, file=sys.stderr)

    for num, value in enumerate(iterable, 1):
        print_progress(num, '\r')
        yield value

    print_progress(num, '\n')
