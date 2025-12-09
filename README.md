# PortMan (Portfolio Manager)
![Project Status](https://img.shields.io/badge/status-MVP-green)
![Streamlit](https://img.shields.io/badge/Streamlit-powered-orange)
![License](https://img.shields.io/badge/license-TBD-lightgrey)

PortMan is a lightweight, local portfolio manager (MVP) that replaces error-prone Excel workflows with a consistent, audited system for recording transactions, tracking position statuses, and computing portfolio KPIs in real time. The app focuses on accurate WAC-based calculations, oversell protection, filter-aware KPIs, CSV exports, and a secure single-user login.

## Table of Contents
- [Project description](#project-description)
- [Tech stack](#tech-stack)
- [Getting started locally](#getting-started-locally)
- [Available scripts](#available-scripts)
- [Project scope](#project-scope)
- [Project status](#project-status)
- [License](#license)

## Project description

PortMan allows quick CRUD of buy/sell/dividend/interest transactions, manual current price updates per ticker, and immediate recalculation of Invested, Realized P/L, Unrealized P/L, and Total P/L (including percentage of Invested when available). The table supports filters (ticker, type, status, instrument category, CFD flag), sorting, and infinite scroll for up to ~100 records. Oversell is blocked via real-time validation, and end users can export the ledger to CSV (`portman-transactions-YYYYMMDD-HHMM.csv`). Local authentication with hashed passwords keeps the single-user experience secure.

For full requirements, see [PRD.md](PRD.md).

## Tech stack

- **Frontend**: Streamlit for rapid UI construction, filters, modals, and in-app CSV export actions.
- **Backend & database**: Python drivers with SQLite as the local store, SQLModel/SQLAlchemy for models, plus hashing (bcrypt/passlib) for authentication logic.
- **Data & utilities**: Pandas, NumPy, pyarrow, and Plotly/Altair assist with data handling and visual summaries as needed.
- **CI/CD**: GitHub Actions is the chosen automation channel for linting, testing, and deployment flows.
- **Dependencies**: Install via `requirements.txt`, which pins Streamlit, SQLModel, pydantic, pytest, and supporting libraries (aiosqlite, requests, typing extensions, etc.).

## Getting started locally

1. **Prerequisites**
   - Python 3.11+ (or the latest 3.x compatible release).
   - `git` for cloning and `pip` for dependency management.

2. **Clone & install**
   ```bash
   git clone <repository-url>
   cd 10x-PortMan
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Initialize the app (optional)**
   - Ensure the default SQLite file (e.g., `portman.db`) is writable in the repo root.
   - Create a single login user via the app’s onboarding modal or script that generates a hashed password; see `app.py` for the hash method (bcrypt/argon2-compatible).

4. **Run**
   ```bash
   streamlit run app.py
   ```
   - Log in with your local credentials, add transactions, define current prices, and verify KPI updates.
   - Use filters/sorting to tailor the table view and export CSV via the action button.

## Available scripts

- `streamlit run app.py` — launches the Streamlit interface and session state logic.
- `python -m pytest tests` — executes the automated test suite (data validation, KPI calculations, etc.).
- `pip install -r requirements.txt` — installs all pinned production and development dependencies.

## Project scope

- **In scope (MVP)**: CRUD of buy/sell/dividend/interest records with CFD flag, oversell blocking, manual current price updates, WAC-based KPI recalculations, filter-aware KPI/transaction table, infinite scrolling up to ~100 records, CSV export with mandated columns, and single-user local authentication.
- **Out of scope for MVP**: Broker/API integrations, advanced reporting dashboards, tax/risk analytics, multi-role permissions, AI assistance, or an explicit ticker-level positions view beyond the aggregated KPI/status logic.
- **Future considerations**: CSV snapshots of prices/positions, refined percent metrics per KPI view, expanded CFD-specific handling, and any API integrations that exceed the MVP boundary.

## Project status

- **MVP stage**: Workflows are designed to mirror existing Excel logic within ±0.01 PLN for all P/L calculations, with a goal of adding a transaction in ≤20 seconds and maintaining smooth interaction with ~100 records.
- **Success metrics**: Zero oversell incidents under tests, filtered/exported data integrity (100% of visible records), responsive filtering/sorting (<200 ms), and accurate KPI recalculations tied to current ticks/prices.
- **Next unlocks**: Extend audit trails for edits/deletions, refine auth session handling, and document GitHub Actions CI steps once configured.

## License

This project does not yet specify a license; please add one (e.g., MIT, Apache 2.0) to clarify reuse terms.
