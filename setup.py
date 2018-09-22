# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    requirements = f.read()

setup(
    name='redmine-cli',
    version='0.1.0',
    description='Command line interface for Redmine',
    long_description=readme,
    author='Ege Güneş',
    author_email='egegunes@gmail.com',
    url='https://github.com/egegunes/redmine-cli',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        redmine=redmine.cli:cli
    '''
)
