all: ruff

ruff:
	uv run --dev ruff format
	uv run --dev ruff check --fix --unsafe-fixes

check:
	uv run --dev basedpyright .

test:
	uv run --dev coverage run -m pytest

coverage:
	uv run --dev coverage report

test-docs:
	uv run --dev sphinx-autobuild docs/source docs/_build/html
