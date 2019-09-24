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

The bot should run out of box, without any required arguments to specify.
However, you may find the following options useful to test the bot before
running it full-scale:

- `--dry-run` - don't perform any actions in Wikidata, just report what's going to be done
- `--verbose` - mention all projects retrieved from Repology, even they don't require any actions
- `--from`, `--to` - limit operation to specific subset of projects

An example output:

```
% ./repology-wikidata-bot.py --from b --to bad --dry-run --verbose
===> babel-llnl (Q4837697)
no action needed
===> babel.js (Q55604651)
Packages/arch (P3454): babel-cli not present in Repology, needs investigation
===> babl (Q28941635)
Packages/aur (P4162): adding babl-git
===> backintime (Q4839110)
Packages/aur (P4162): adding backintime-cli-git
Packages/aur (P4162): adding backintime-git
Packages/aur (P4162): adding backintime-cli
===> backuppc (Q798540)
Packages/gentoo (P3499): adding app-backup/backuppc
===> bacula (Q591063)
Packages/aur (P4162): adding bacula-console
Packages/aur (P4162): adding bacula-fd
Packages/aur (P4162): adding bacula-dir-sqlite3
Packages/aur (P4162): adding bacula-common
Packages/aur (P4162): adding bacula-bat
Packages/aur (P4162): adding bacula-client
Packages/aur (P4162): adding bacula-dir-mysql
Packages/aur (P4162): adding bacula-dir-postgresql
Packages/aur (P4162): adding bacula5-client
Packages/aur (P4162): adding bacula-sd
Packages/aur (P4162): adding bacula-dir
Packages/aur (P4162): adding bacula-dir-mariadb
```

## Links

* [List of projects](https://repology.org/projects/?inrepo=wikidata) linked to Wikidata in Repology
* Bot's [User page](https://www.wikidata.org/wiki/User:Repology_bot) on Wikidata
* Author's [User page](https://www.wikidata.org/wiki/User:AMDmi3) on Wikidata

## Author

* [Dmitry Marakasov](https://github.com/AMDmi3) <amdmi3@amdmi3.ru>

## License

GPLv3 or later, see [COPYING](COPYING).
