
POETRY_VERSION := 1.8.3
CLI_NAME := "oss4energy.cli"

.PHONY: install
install:
	pip install pipx
	pipx ensurepath
	pipx install poetry==$(POETRY_VERSION) || echo "Poetry already installed"
	poetry config virtualenvs.create true 
	poetry install --all-extras --no-cache
	python -m spacy download en_core_web_sm
	
.PHONY: add
add:
	typer $(CLI_NAME) run add

.PHONY: build
build:
	poetry lock

.PHONY: discover
discover:
	typer $(CLI_NAME) run discover

.PHONY: generate_listing
generate_listing:
	# Note: typer processes "_" as "-"
	typer $(CLI_NAME) run generate-listing	

.PHONY: publish
publish:
	typer $(CLI_NAME) run publish

.PHONY: search
search:
	typer $(CLI_NAME) run search

.PHONY: help
help:
	typer $(CLI_NAME) run --help