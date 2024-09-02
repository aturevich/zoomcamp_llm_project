.PHONY: install test run format lint

install:
	pipenv install --dev

test:
	pipenv run pytest

run:
	pipenv run uvicorn src.main:app --reload

format:
	pipenv run black .

lint:
	pipenv run flake8 .

setup: install format lint test