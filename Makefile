.PHONY: install
install:
	@uv sync --locked
	@uv run --locked prek install --hook-type pre-commit --hook-type commit-msg

.PHONY: update
update:
	@uv lock --upgrade
	@uv sync --locked
	@uv run --locked prek update

.PHONY: format
format:
	@uv run --locked ruff check --fix .
	@uv run --locked ruff format .

.PHONY: lint
lint:
	@uv run --locked prek run --all-files

.PHONY: test
test:
	@uv run --locked python -m unittest

.PHONY: notebook
notebook:
	@uv run --locked jupyter nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=60 --stdout examples.ipynb > /dev/null

.PHONY: package
package:
	@uv build

.PHONY: docs-wheel
docs-wheel:
	@uv run --locked python scripts/prepare_docs_wheel.py

.PHONY: docs
docs: docs-wheel
	@uv run --locked zensical build --clean --config-file zensical.toml
	@uv run --locked zensical build --clean --config-file zensical.en.toml
	@uv run --locked python scripts/build_localized_docs.py
	@uv run --locked python scripts/verify_docs_build.py

.PHONY: docs-a11y
docs-a11y: docs
	@bash scripts/check_docs_accessibility.sh

.PHONY: docs-serve
docs-serve: docs-wheel
	@uv run --locked zensical serve --config-file zensical.toml

.PHONY: docs-serve-en
docs-serve-en: docs-wheel
	@uv run --locked zensical serve --config-file zensical.en.toml

.PHONY: build
build: package docs

.PHONY: check
check: lint test notebook build
