PACKAGE_DIR := peano/

.PHONY: install
install:
	@poetry install
	@poetry run pre-commit install

.PHONY: update
update:
	@poetry show -o --only=dev --top-level --no-ansi -f json | python3 -c 'import json,sys; print("\n".join(pkg["name"] for pkg in json.load(sys.stdin)))' > temp_dev.txt
	@[ -s temp_dev.txt ] && xargs poetry add --group dev < temp_dev.txt || true
	@rm temp_dev.txt
	@poetry update
	@poetry run pre-commit autoupdate

.PHONY: lint
lint:
	@poetry run pre-commit run --all-files

.PHONY: test
test:
	@poetry run python -m unittest
