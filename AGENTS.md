# Repository Guidelines

## Project Structure & Module Organization
The repository centers on analytical pipelines for SPY option chains. Keep production code inside `src/`, using files such as `src/greeks_calculator.py`, `src/anomaly_detector.py`, `src/strategy.py`, and `src/backtest.py` as extension points. Reproducible notebooks live in `notebooks/`, while raw datasets are regenerated into `data/raw/` via `data/get_data.py`; avoid committing CSV outputs because the directory is gitignored. Document assets, dictionaries, and strategy notes under `docs/`. Automated tests mirror the source layout inside `tests/`, and sample submission artefacts belong in `sample_submission/`.

## Build, Test, and Development Commands
Create a local environment with `python3 -m venv .venv && source .venv/bin/activate`. Install dependencies after editing `requirements.txt` via `pip install -r requirements.txt`. Generate the deterministic research dataset by running `python data/get_data.py`. Execute linters with `ruff check src tests` (add Ruff if adopted) and auto-format with `black src tests`. Run the unit suite through `pytest --maxfail=1 -q`.

## Coding Style & Naming Conventions
Target Python 3.11+, adhere to PEP 8, and use four-space indentation. Modules should expose typed interfaces; add `from __future__ import annotations` to new files. Favor snake_case for functions, PascalCase for classes, and suffix Greeks calculators with `_greeks`. Keep notebook filenames date-prefixed (e.g., `2024-04-12_iv_smile.ipynb`). Document nontrivial functions with Google-style docstrings and include units where relevant.

## Testing Guidelines
Adopt pytest with fixtures under `tests/fixtures`. Name test files `test_<module>.py` and tests `test_<behavior>`. Validate Greeks numerically using finite-difference backstops and aim for >=85% coverage with `pytest --cov=src --cov-report=term-missing`. Record deterministic seeds when mocking randomness. Attach sample CSVs under `tests/data` and keep them below 1 MB.

## Commit & Pull Request Guidelines
Use Conventional Commits (`feat`, `fix`, `refactor`, `test`) to aid future release notes. Each PR should describe the dataset snapshot used, summarize validation steps, and link to the motivating issue or research note. When visuals change, attach updated figures in the PR body. Request review before merging; require one approval plus a green CI run.

## Data Security & Configuration
Store credentials and API tokens in `.env` or system keychains—never commit secrets. The synthetic dataset generator keeps `data/raw/` out of source control; maintain that behaviour. Document environment variables in `docs/configuration.md` if new integrations appear, and provide sanitized samples in `.env.example`. When distributing derived datasets or notebooks, strip PII and limit to fields referenced in the README tasks.
