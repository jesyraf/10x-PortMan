# Database Plan for PortMan (SQLite)

1. **Tables with columns, data types, and constraints**
- **users**
  - `id INTEGER PRIMARY KEY AUTOINCREMENT`
  - `login TEXT NOT NULL UNIQUE`
  - `password_hash TEXT NOT NULL`
  - `created_at TEXT NOT NULL DEFAULT (datetime('now'))`
  - `last_login TEXT`
  - `failed_attempts INTEGER NOT NULL DEFAULT 0 CHECK(failed_attempts >= 0)`
  - `locked_until TEXT`
  - Purpose: single local account; fields support future lockouts and session tracking.

- **transactions**
  - `id INTEGER PRIMARY KEY AUTOINCREMENT`
  - `user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE`
  - `transaction_date TEXT NOT NULL` (ISO 8601)
  - `ticker TEXT NOT NULL COLLATE NOCASE`
  - `type TEXT NOT NULL CHECK(type IN ('buy','sell','dividend','interest'))`
  - `quantity NUMERIC CHECK(quantity >= 0)` (required for buy/sell)
  - `unit_price NUMERIC CHECK(unit_price >= 0)` (required for buy/sell)
  - `cash_value NUMERIC NOT NULL CHECK(cash_value >= 0)` (buy/sell: quantity × unit_price; dividends/interest: gross amount)
  - `currency TEXT NOT NULL DEFAULT 'PLN' CHECK(currency = 'PLN')`
  - `category TEXT NOT NULL CHECK(category IN ('stock','ETF','bond','other'))`
  - `cfd_flag INTEGER NOT NULL DEFAULT 0 CHECK(cfd_flag IN (0,1))`
  - `status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','archived'))`
  - `notes TEXT`
  - `created_at TEXT NOT NULL DEFAULT (datetime('now'))`
  - `updated_at TEXT NOT NULL DEFAULT (datetime('now'))`
  - `CHECK (
      (type IN ('buy','sell') AND quantity IS NOT NULL AND unit_price IS NOT NULL)
      OR (type IN ('dividend','interest') AND quantity IS NULL AND unit_price IS NULL)
    )`
  - `CHECK (type NOT IN ('buy','sell') OR ABS(cash_value - (quantity * unit_price)) < 0.01)` (keeps cash_value consistent within tolerance)
  - Notes: all `quantity`, `unit_price`, and `cash_value` use `NUMERIC` (DECIMAL 18,4 semantics) to preserve precision; `currency` is currently limited to PLN but can be extended later.

- **current_prices**
  - `ticker TEXT PRIMARY KEY COLLATE NOCASE`
  - `current_price NUMERIC NOT NULL CHECK(current_price >= 0)`
  - `currency TEXT NOT NULL DEFAULT 'PLN' CHECK(currency = 'PLN')`
  - `updated_at TEXT NOT NULL DEFAULT (datetime('now'))`
  - `source TEXT NOT NULL DEFAULT 'manual'`
  - Purpose: one row per ticker, overwritten on each price update to drive Unrealized/Total P/L.

- **ticker_positions** (cached aggregates maintained via triggers)
  - `ticker TEXT PRIMARY KEY COLLATE NOCASE`
  - `user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE`
  - `net_quantity NUMERIC NOT NULL DEFAULT 0 CHECK(net_quantity >= 0)`
  - `total_cost_basis NUMERIC NOT NULL DEFAULT 0 CHECK(total_cost_basis >= 0)`
  - `average_cost NUMERIC GENERATED ALWAYS AS (
      CASE WHEN net_quantity > 0 THEN total_cost_basis / net_quantity ELSE NULL END
    ) STORED`
  - `realized_pl NUMERIC NOT NULL DEFAULT 0`
  - `updated_at TEXT NOT NULL DEFAULT (datetime('now'))`
  - Purpose: keep WAC, net quantity, and realized P/L per ticker readily available for queries and validations, ensuring buy/sell aggregates remain consistent under the oversell guard.

2. **Relationships between tables**
- `users (1)` → `transactions (many)` ensures every transaction is tied to the local account; `ON DELETE CASCADE` keeps data clean if account is recreated.
- `transactions (many)` → `ticker_positions (1)` via `ticker` (maintained by triggers) to enforce one aggregated row per ticker per user.
- `current_prices (1)` ↔ `ticker_positions (1)` by `ticker` for joining when computing Unrealized P/L; the application joins the two for KPI views.

3. **Indexes**
- `CREATE INDEX idx_transactions_ticker ON transactions(ticker)` to speed ticker filters and joins with price/position aggregates.
- `CREATE INDEX idx_transactions_type_status ON transactions(type, status)` to accelerate filtered KPI queries and status-based lists.
- `CREATE INDEX idx_transactions_category ON transactions(category)` for fast category filters (stock/ETF/bond/other).
- `CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC)` to support infinite scroll and fast sort-by-date.
- `CREATE INDEX idx_transactions_ticker_created_at ON transactions(ticker, created_at DESC)` to serve ticker-specific views like filtered KPIs or per-ticker historical audits.
- `CREATE INDEX idx_transactions_user_type ON transactions(user_id, type)` to future-proof multi-account support and speed user-scoped reports.
- Primary keys on `current_prices` and `ticker_positions` double as unique indexes and cover lookup needs.

4. **SQLite-specific policies and structures**
- Row-level security is not applicable: the MVP targets one local user with SQLite-backed authentication, so the application enforces access control.
- **Oversell enforcement trigger**: an `AFTER INSERT OR UPDATE OR DELETE ON transactions` trigger recalculates `ticker_positions` aggregates and aborts with `RAISE(ABORT, 'oversell detected')` when total sells exceed total buys, providing the error message required for UI feedback.
- **KPI view for reference** (`portfolio_kpis`):
  ```sql
  CREATE VIEW portfolio_kpis AS
  SELECT
    SUM(CASE WHEN type = 'buy' THEN quantity * unit_price ELSE 0 END) AS invested,
    SUM(CASE WHEN type = 'sell' THEN cash_value - (quantity * average_cost) ELSE 0 END) +
      SUM(CASE WHEN type IN ('dividend','interest') THEN cash_value ELSE 0 END) AS realized_pl,
    SUM(tl.net_quantity * cp.current_price - tl.net_quantity * tl.average_cost) AS unrealized_pl,
    (SUM(CASE WHEN type = 'sell' THEN cash_value - (quantity * average_cost) ELSE 0 END) +
      SUM(CASE WHEN type IN ('dividend','interest') THEN cash_value ELSE 0 END)) +
    SUM(tl.net_quantity * (cp.current_price - tl.average_cost)) AS total_pl
  FROM transactions
  LEFT JOIN ticker_positions tl ON tl.ticker = transactions.ticker
  LEFT JOIN current_prices cp ON cp.ticker = transactions.ticker;
  ```
  This view is a template for the filtered queries performed by the frontend; filters are applied in the `WHERE` clause there, keeping KPI definitions consistent with the PRD.

5. **Additional notes and design rationales**
- Aggregated `ticker_positions` accelerates WAC/oversell calculations, enabling real-time validation without scanning all historical transactions each time.
- The schema uses explicit `CHECK` constraints and `NUMERIC` columns to model the required decimal precision (DECIMAL 18,4) while preventing negatives across amounts, prices, and cash values.
- Triggers maintain aggregates and oversell guards while keeping the frontend logic simple: the client sends intended transaction data, and the database raises a descriptive error when oversell rules are violated.
- Indexes focus on the common filters (ticker, type, status, category) described in the PRD to keep pagination, filtering, and sorting snappy even near the ~100-transaction target.
- Currency is restricted to PLN per MVP but could expand by removing the `CHECK` in a future stage when multi-currency support is needed.
