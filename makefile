
POETRY_VERSION := 1.8.3
CLI_NAME := "oss4climate.cli"

.PHONY: install
install:
	curl -LsSf https://astral.sh/uv/install.sh | sh
	source $HOME/.cargo/env
	uv sync
	python -m spacy download en_core_web_sm || echo "Failed download of Spacy model"
	
.PHONY: install_dev
install_dev:
	poetry install --all-extras --no-cache
	pre-commit install

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

.PHONY: run_app
run_app:
	gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080 app:app

.PHONY: help
help:
	typer $(CLI_NAME) run --help

.PHONY: test
test:
	pytest src/test/.