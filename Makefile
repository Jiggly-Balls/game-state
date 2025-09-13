all: ruff

ruff:
	uv tool run ruff format
	uv tool run ruff check --fix

check:
	uv tool run basedpyright .
