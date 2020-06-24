# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

setup(
    name="redminecli",
    version="1.3.0",
    description="Command line interface for Redmine",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Ege Güneş",
    author_email="egegunes@gmail.com",
    url="https://github.com/egegunes/redmine-cli",
    license="GPLv3",
    packages=find_packages(exclude=("tests", "docs")),
    install_requires=["requests>=2.22.0", "click>=7.0", "colorama>=0.4.1"],
    entry_points="""
        [console_scripts]
        redmine=redmine.cli.main:cli
    """,
)
