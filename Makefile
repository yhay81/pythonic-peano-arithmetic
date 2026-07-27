.PHONY: install
install:
	@uv sync
	@uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

.PHONY: update
update:
	@uv lock --upgrade
	@uv sync
	@uv run pre-commit autoupdate

.PHONY: format
format:
	@uv run ruff check --fix .
	@uv run ruff format .

.PHONY: lint
lint:
	@uv run pre-commit run --all-files

.PHONY: test
test:
	@uv run python -m unittest

.PHONY: notebook
notebook:
	@uv run jupyter nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=60 --stdout examples.ipynb > /dev/null

.PHONY: build
build:
	@uv build

.PHONY: check
check: lint test notebook build
