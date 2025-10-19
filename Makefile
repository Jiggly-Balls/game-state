all: ruff

ruff:
	uv tool run ruff format
	uv tool run ruff check --fix

check:
	uv tool run basedpyright .

test-docs:
	uv run sphinx-autobuild docs/source docs/_build/html
