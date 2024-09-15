# Variables
PYTHON = python3
PIP = pip3
DOCKER_COMPOSE = docker-compose -f docker/docker-compose.yml

# Commands
.PHONY: setup install run test format lint docker-up docker-down clean requirements

setup: install

install:
	pipenv install --dev

run:
	pipenv run uvicorn src.api.main:app --reload

test:
	pipenv install --dev
	pipenv run python -m pytest tests

format:
	pipenv run black src tests

lint:
	pipenv run flake8 src tests

docker-up:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

requirements:
	pipenv lock

# Default target
all: setup
