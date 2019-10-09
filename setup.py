#!/usr/bin/env python3

from setuptools import setup


def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line for line in f.readlines() if not line.startswith('-')]


setup(
    name='repology-wikidata-bot',
    version='0.0.0',
    description='Bot to fill Wikidata entries with data from Repology',
    author='Dmitry Marakasov',
    author_email='amdmi3@amdmi3.ru',
    url='https://repology.org/',
    license='GNU General Public License v3 or later (GPLv3+)',
    scripts=[
        'repology-wikidata-bot.py',
    ],
    data_files={
        'blacklist': ['blacklist.txt'],
    },
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Wiki',
        'Topic :: System :: Archiving :: Packaging',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.7',
    install_requires=read_requirements('requirements.txt')
)
