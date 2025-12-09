# Database PRD Summary

## Decisions made
- Store transactions in a single `transactions` table with typed columns (id, ticker, type, amount, price, value, currency, category, CFD flag, status, notes, timestamps) plus DECIMAL(18,4) and CHECK constraints avoiding negative values.
- Maintain a single current price record per ticker, overwriting on each update (`current_price`, `currency`, `updated_at`, PLN only).
- Restrict instrument categories to the predefined set and enforce oversell prevention via database `CHECK` constraints.
- Support KPI calculations (Invested, Realized, Unrealized, Total) through materialized views or cached aggregations to keep filtered responsiveness.
- CSV export respects current filters, follows defined column ordering, and uses filenames like `portman-transactions-YYYYMMDD-HHMM.csv`.
- MVP remains single-user with local authorization, so no RLS or multi-account schema is required.

## Recommendations aligned with discussion
1. Define `transactions` with DECIMAL(18,4) for monetary values, NOT NULL for required fields, type-driven constraints (e.g., `price` nullable for dividend/interest), and checks ensuring `amount`, `price`, `value` are ≥ 0.
2. Introduce `prices` as a single-row-per-ticker table (`current_price`, PLN currency, `updated_at`) and index `ticker` for fast joins when computing Unrealized P/L.
3. Implement oversell validation inside the database (via CHECK or triggers) so `sell` inserts/updates are blocked when the sum of sells surpasses buys, enabling precise client messaging about available volume.
4. Create multi-column indexes on `ticker`, `type`, `status`, `category`, `created_at` plus partial indexes focused on buy/sell transactions to speed filtering, sorting, and oversell aggregation.
5. Use materialized views or maintained aggregations for Invested/Realized/Unrealized/Total KPIs to ensure KPI values update immediately after transaction or price changes, even under filtered queries.
6. Build CSV export via a SELECT that orders the mandated columns and lets the app craft the timestamped filename while ensuring record counts mirror the filtered dataset.

## Unresolved questions
- The exact mechanism for oversell enforcement (how to keep aggregate buy/sell balances consistent during concurrent edits) still needs clarification for the implementation layer.
- While the current plan overwrites ticker prices, consider future extensions for storing price history or versioning if requirements evolve.
