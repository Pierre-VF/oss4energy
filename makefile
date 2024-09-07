
POETRY_VERSION := 1.8.3

.PHONY: install
install:
	pip install pipx
	pipx ensurepath
	pipx install poetry==$(POETRY_VERSION) || echo "Poetry already installed"
	poetry config virtualenvs.create true 
	poetry install --all-extras --no-cache

.PHONY: build
build:
	poetry lock