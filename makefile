
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

.PHONY: discover
discover:
	typer scripts/cli.py run discover	
	typer scripts/cli.py run format

.PHONY: generate_listing
generate_listing:
	# Note: typer processes "_" as "-"
	typer scripts/cli.py run generate-listing	
	typer scripts/cli.py run format

.PHONY: publish
publish:
	typer scripts/cli.py run publish

.PHONY: help
help:
	typer scripts/cli.py run --help