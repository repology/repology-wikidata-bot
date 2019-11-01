FLAKE8?=	flake8
MYPY?=		mypy

STATICDIR=	repologyapp/static

all:: lint

lint:: flake8 mypy

flake8::
	${FLAKE8}

mypy::
	${MYPY} --strict repology-wikidata-bot.py

run:
	./repology-wikidata-bot.py --html report.html
