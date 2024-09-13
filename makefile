
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

.PHONY: update_list
update_list:
	python scripts/generate_index.py
	black repo_index.toml

.PHONY: run
run:
	python scripts/generate_data.py
	black .data/summary.toml

.PHONY: publish
publish:
	python scripts/publish_datasets.py

.PHONY: help
help:
	typer scripts/cli.py run --help