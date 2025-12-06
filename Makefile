all: ruff

ruff:
	uv run ruff format
	uv run ruff check --fix

check:
	uv run basedpyright .

test-docs:
	uv run sphinx-autobuild docs/source docs/_build/html
