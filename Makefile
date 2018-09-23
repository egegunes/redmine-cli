requirements:
	pip install -r requirements.txt

dev-requirements:
	pip install -r dev-requirements.txt

check:
	flake8 redmine/*
	isort redmine/*

install:
	pip install -e .

test:
	pytest

coverage:
	pytest --cov=redmine
