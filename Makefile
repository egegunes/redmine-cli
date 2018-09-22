requirements:
	pip install -r requirements.txt

check:
	flake8 redmine/*
	isort-3 redmine/*

