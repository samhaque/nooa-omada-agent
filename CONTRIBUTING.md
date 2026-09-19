# Contributing

## Setup

```bash
uv sync
cp .env.example .env   # fill in NEMOTRON_BASE_URL
```

Needs a checkout of [omada-controller-mcp](https://github.com/samhaque/omada-controller-mcp)
as a sibling directory, see `README.md`.

## Tests

Plain `assert` scripts, pytest-discovered, no network calls:

```bash
uv run pytest
```

Add new tests as `test_*.py` functions following this pattern.

## Style

```bash
uv run ruff check .
uv run ruff format .
```

## Changelog

User-facing changes get an entry in `CHANGELOG.md` (Keep a Changelog format, semver tags).
