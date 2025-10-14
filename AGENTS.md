# Repository Guidelines

## Project Structure & Module Organization
The repository centers on analytical pipelines for SPY option chains. Place production code inside `src/`, separated into `src/data_ingest` for loaders, `src/models` for Greeks and pricing utilities, and `src/strategies` for trading logic. Reproducible notebooks belong in `notebooks/`; export cleaned datasets to `data/processed` while keeping raw partner feeds in `data/raw`. CLI or cron-entry scripts, including the provided SPY downloader, should live in `scripts/`. Keep experiment write-ups and diagrams under `docs/`. Automated tests mirror package layout inside `tests/`.

## Build, Test, and Development Commands
Create a local environment with `python3 -m venv .venv && source .venv/bin/activate`. Install dependencies after editing `requirements.txt` via `pip install -r requirements.txt`. Fetch or refresh SPY data by running `python scripts/fetch_spy_data.py --days 20`. Execute the research CLI with `python -m src.cli` once built. Run static checks using `ruff check src tests` and auto-format with `black src tests`. Launch the full suite through `pytest --maxfail=1 -q`.

## Coding Style & Naming Conventions
Target Python 3.11+, adhere to PEP 8, and use four-space indentation. Modules should expose typed interfaces; add `from __future__ import annotations` to new files. Favor snake_case for functions, PascalCase for classes, and suffix Greeks calculators with `_greeks`. Keep notebook filenames date-prefixed (e.g., `2024-04-12_iv_smile.ipynb`). Document nontrivial functions with Google-style docstrings and include units where relevant.

## Testing Guidelines
Adopt pytest with fixtures under `tests/fixtures`. Name test files `test_<module>.py` and tests `test_<behavior>`. Validate Greeks numerically using finite-difference backstops and aim for >=85% coverage with `pytest --cov=src --cov-report=term-missing`. Record deterministic seeds when mocking randomness. Attach sample CSVs under `tests/data` and keep them below 1 MB.

## Commit & Pull Request Guidelines
Use Conventional Commits (`feat`, `fix`, `refactor`, `test`) to aid future release notes. Each PR should describe the dataset snapshot used, summarize validation steps, and link to the motivating issue or research note. When visuals change, attach updated figures in the PR body. Request review before merging; require one approval plus a green CI run.

## Data Security & Configuration
Store credentials and API tokens in `.env` or system keychains—never commit secrets. Add `.env` and raw data directories to `.gitignore`. Document environment variables in `docs/configuration.md` and provide sanitized samples in `.env.example`. When sharing datasets, strip PII and limit to fields referenced in the README tasks.
