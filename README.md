# YO_graph

`YO_graph` is a small Python project that generates a static web dashboard for Finnish matriculation exam thresholds.

It fetches official YTL point-threshold tables, normalizes each grade cutoff by the subject's maximum score, and writes a single HTML file you can open locally or deploy as a static site.

## What It Does

For each supported subject, the app:

1. Fetches YTL point-threshold pages from 2021 onward.
2. Extracts the score cutoffs for grades `L`, `E`, `M`, `C`, `B`, and `A`.
3. Normalizes each cutoff to a `0..1` scale using the subject's maximum points.
4. Builds a browser dashboard with a subject selector and an all-grades time-series chart.

The project is YTL-only. YLE support was removed because the live YLE site no longer provides reliable multi-semester survey coverage.

## Project Layout

- [main.py](/home/me/code/self/yograph/main.py): entrypoint, subject configuration, and HTML generation
- [dashboard.py](/home/me/code/self/yograph/dashboard.py): payload building and dashboard rendering
- [ytl.py](/home/me/code/self/yograph/ytl.py): YTL scraping and threshold parsing
- [lib.py](/home/me/code/self/yograph/lib.py): shared types and cached async HTTP client
- [tests/test_ytl.py](/home/me/code/self/yograph/tests/test_ytl.py): parser-level tests
- [tests/test_dashboard.py](/home/me/code/self/yograph/tests/test_dashboard.py): dashboard and output tests
- [tests/test_live_services.py](/home/me/code/self/yograph/tests/test_live_services.py): live YTL integration checks

## Supported Subjects

- Matematiikka (pitkä)
- Fysiikka
- Kirjoitustaito (suomi)
- Lukutaito (suomi)
- Kemia
- Englanti (pitkä)
- Maantiede
- Biologia

## Running Locally

This project uses Python 3.13 and `uv`.

```bash
uv sync
uv run python main.py
```

That writes `dashboard.html` in the repository root and opens it in your browser.

## Static Deployment

This app is a static-site generator, not a long-running web service.

To produce a deployable artifact:

```bash
mkdir -p dist
uv run python - <<'PY'
import asyncio
from main import main
async def run():
    await main(output_path="dist/index.html")
asyncio.run(run())
PY
```

The result is a single static file:

- `dist/index.html`

The page embeds its data inline and loads Chart.js from jsDelivr at runtime.

## Testing

Run the automated tests with:

```bash
./.venv/bin/python -m unittest discover -s tests -v
./.venv/bin/python -m compileall main.py dashboard.py lib.py ytl.py tests
```

The live integration tests access the public YTL website directly.

## Notes

- No secrets or API keys are required.
- Network access is required when generating the dashboard.
- HTTP requests are cached in [lib.py](/home/me/code/self/yograph/lib.py) to reduce repeated load on the upstream site during development.
