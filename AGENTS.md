# Repository Guidelines

## Project Structure & Module Organization
This repository is a small Python 3.13 project with a flat layout. `main.py` is the entrypoint, `ytl.py` fetches and parses YTL point-threshold tables, `dashboard.py` builds the browser UI, and `lib.py` holds shared types plus the cached async HTTP client. Project metadata lives in `pyproject.toml`, with locked versions in `uv.lock`. Tests live under `tests/`.

## Build, Test, and Development Commands
Use `uv` for environment management and execution.

- `uv sync`: install or update dependencies from `pyproject.toml` and `uv.lock`
- `uv run python main.py`: fetch live YTL data, generate `dashboard.html`, and open it
- `./.venv/bin/python -m unittest discover -s tests -v`: run unit and live integration tests
- `./.venv/bin/python -m compileall main.py dashboard.py lib.py ytl.py tests`: quick syntax smoke test

## Coding Style & Naming Conventions
Follow the existing style: 4-space indentation, explicit imports, and small top-level modules. Use `snake_case` for functions and variables, `PascalCase` for `NamedTuple` types like `Subject` and `YtlDatum`, and keep scraping helpers focused on one parsing task at a time. Prefer plain data structures for dashboard payloads so the front-end script stays easy to inspect.

## Testing Guidelines
The test suite covers YTL parsing, dashboard payload generation, HTML rendering, and live YTL integration. Add new tests under `tests/` with `test_*.py` names. When changing scraping logic, include at least one fixture-style unit test and keep the live checks passing.

## Commit & Pull Request Guidelines
Recent commits use short, imperative summaries such as `refactoring` and `change example to english`. Keep commit messages brief, describe one logical change per commit, and include manual verification details in pull requests when the dashboard output changes.

## Security & Configuration Tips
This project calls public YTL endpoints only and does not require secrets. Preserve the caching behavior in `lib.py` so repeated development runs do not hit the upstream service unnecessarily.
