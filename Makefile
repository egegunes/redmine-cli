requirements:
	pip install -r requirements.txt

dev-requirements:
	pip install -r dev-requirements.txt

lint:
	flake8 redmine/ tests/
	isort -rc -c redmine/ tests/

install:
	pip install -e .

test:
	pytest

coverage:
	pytest --cov=redmine
