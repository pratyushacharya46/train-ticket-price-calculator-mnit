set shell := ["powershell.exe", "-c"]


ARGS_TEST := env("_UV_RUN_ARGS_TEST", "")

@_:
    just --list


# Run tests
[group('qa')]
test *args:
    uv run {{ ARGS_TEST }} pytest --cov=src --cov-report=html --cov-branch --cov-fail-under=90 --tb=line -v {{ args }}

# Run linters
[group('qa')]
lint:
    uvx ruff format
    uvx ruff check --fix
