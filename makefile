
POETRY_VERSION := 1.8.3
CLI_NAME := "oss4energy.cli"

.PHONY: install
install:
	pip install pipx
	pipx ensurepath
	pipx install poetry==$(POETRY_VERSION) || echo "Poetry already installed"
	poetry config virtualenvs.create true 
	poetry install --no-cache
	python -m spacy download en_core_web_sm || echo "Failed download of Spacy model"
	
.PHONY: install_dev
install:
	poetry install --all-extras --no-cache

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

.PHONY: download_data
download_data:
	typer $(CLI_NAME) run download-data

.PHONY: help
help:
	typer $(CLI_NAME) run --help

.PHONY: test
test:
	pytest src/test/.