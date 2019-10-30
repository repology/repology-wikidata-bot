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
import time
from datetime import timedelta
from typing import Any, Iterable


def progressify(iterable: Any, message: str) -> Iterable[Any]:
    num_total = len(iterable) if hasattr(iterable, '__len__') else None
    num_done = 0
    it = iter(iterable)
    start_time = time.monotonic()

    def print_progress(end: str) -> None:
        if num_total is None:
            print('{} [{}]...'.format(message, num_done), end=end, file=sys.stderr)
            return

        elapsed_seconds = time.monotonic() - start_time

        if elapsed_seconds >= 1.0 and num_done >= 1:
            remaining_seconds = elapsed_seconds * (num_total - num_done) / num_done
            print('{} [{}/{}, {} remaining]... '.format(message, num_done, num_total, timedelta(seconds=int(remaining_seconds))), end=end, file=sys.stderr)
            return

        print('{} [{}/{}]...'.format(message, num_done, num_total), end=end, file=sys.stderr)

    while True:
        print_progress('\r')

        try:
            yield next(it)
            num_done += 1
        except StopIteration:
            print_progress('\n')  # end with # of items
            return
