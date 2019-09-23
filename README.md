# Repology wikidata bot

[![Build Status](https://travis-ci.org/repology/repology-wikidata-bot.svg?branch=master)](https://travis-ci.org/repology/repology-wikidata-bot)

Update Wikidata entries using information from Repology.

This bot iterates over software projects listed [Repology](https://repology.org) which have associated (by specifying [Repology project name](https://www.wikidata.org/wiki/Property:P6931) property for a software project in Wikidata) Wikidata entry, and fills package information (such as [Gentoo package](https://www.wikidata.org/wiki/Property:P3499) property).

## Dependencies

- [Python](https://www.python.org/) 3.7+
- Python module [pywikibot](https://pypi.org/project/pywikibot/)
- Python module [requests](https://pypi.org/project/requests/)

Modules can be installed with `pip install -r requirements.txt` command.

## Running

The bot is already set up to its wikidata account and Repology API url.

You can run it in _dry-run_ mode right away - it will show what modifications it's going to perform, but won't actually do anything.

```
% ./repology-wikidata-bot.py --dry-run
6tunnel: gentoo (P3499): adding net-vpn/6tunnel
a2jmidid: gentoo (P3499): adding media-sound/a2jmidid
a2ps: gentoo (P3499): adding app-text/a2ps
abiword: gentoo (P3499): adding app-office/abiword-docs
abook: gentoo (P3499): adding app-misc/abook
adom: gentoo (P3499): adding games-roguelike/adom
aerc: gentoo (P3499): adding mail-client/aerc
agda: gentoo (P3499): adding sci-mathematics/agda
agg: gentoo (P3499): adding x11-libs/agg
alacarte: gentoo (P3499): adding x11-misc/alacarte
albert: gentoo (P3499): adding x11-misc/albert
alembic: gentoo (P3499): adding media-gfx/alembic
alienarena: gentoo (P3499): adding games-fps/alienarena
amanda: gentoo (P3499): adding app-backup/amanda
amavisd-new: gentoo (P3499): adding mail-filter/amavisd-new
ampache: gentoo (P3499): adding www-apps/ampache
^C
```

It lists repology project name, and packages list it's going to
add. Without `--dry-run` it will add listed package entries to
wikidata. You can limit it with a subset of packages with `--from`
and `--to` arguments. For instance, `--from a --to b` will only
operate on projects starting with `a`.

## Links

* [List of projects](https://repology.org/projects/?inrepo=wikidata) linked to Wikidata in Repology
* Bot's [User page](https://www.wikidata.org/wiki/User:Repology_bot) on Wikidata
* Author's [User page](https://www.wikidata.org/wiki/User:AMDmi3) on Wikidata

## Author

* [Dmitry Marakasov](https://github.com/AMDmi3) <amdmi3@amdmi3.ru>

## License

GPLv3 or later, see [COPYING](COPYING).
