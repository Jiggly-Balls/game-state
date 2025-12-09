all: ruff

ruff:
	uv run ruff format
	uv run ruff check --fix

check:
	uv run basedpyright .

test:
	uv run coverage run -m pytest

coverage:
	uv run coverage report

test-docs:
	uv run sphinx-autobuild docs/source docs/_build/html
