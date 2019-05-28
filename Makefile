dev-requirements:
	pip install -r dev-requirements.txt
lint:
	flake8 --max-line-length 88 redmine/ tests/
	isort -rc -c redmine/ tests/
install:
	pip install -e .
test:
	pytest
coverage:
	pytest --cov=redmine
bdist:
	python3 setup.py sdist bdist_wheel
upload:
	twine upload dist/*
clean:
	rm -rf build dist *.egg-info venv
