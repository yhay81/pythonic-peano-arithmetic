PACKAGE_DIR := peano/

.PHONY: install
install:
	@poetry install
	@poetry run pre-commit install

.PHONY: update
update:
	@poetry show -o -t | grep -v -e "--" | cut -d " " -f 1 > temp_dev.txt
	@cat temp_dev.txt | xargs poetry add --dev
	@rm temp_dev.txt
	@poetry update
	@poetry run pre-commit autoupdate

.PHONY: lint
lint:
	@poetry run pre-commit run --all-files

.PHONY: test
test:
	@poetry run python -m unittest
