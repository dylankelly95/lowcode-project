## Business problem
As artists sign up and upload portfolios, projects, and attached media assets (`audio`, `image`, `video`) to the Artfolio SQLite database (`app.db`), platform administrators need a quick aggregate overview of active records, projects missing a scheduled `release_date`, and projects with zero attached media files—without manually querying individual tables or producing an unwieldy row-by-row dump.

## Trigger
On-demand CLI execution (`python3 tools/portfolio_digest.py`) or a scheduled daily cron job (`0 9 * * *`) that reads the live `app.db` SQLite database via `db.get_connection()`.

## Steps
1. Open a SQLite connection to `app.db` through `db.get_connection()` with `PRAGMA foreign_keys = ON` enforced.
2. Query total record counts across `users`, `portfolios`, `projects`, and `media`.
3. Run aggregate `COUNT` and `GROUP BY` queries to calculate how many projects lack a `release_date`, how many have zero attached media items, and total counts grouped by `category_medium` and media `file_type`.
4. Format the aggregate summary into a timestamped Markdown report, print it to the terminal, and save it to `docs/portfolio/latest-digest.md`.

## Failure questions
- **What if it fires twice?**
  Because `tools/portfolio_digest.py` only executes read-only `SELECT` queries and overwrites `docs/portfolio/latest-digest.md` with the latest timestamped snapshot, running it twice is completely idempotent—it never creates duplicate rows or mutates `app.db`.
- **What if a step fails halfway?**
  If `app.db` is missing, locked, or schema migrations have not been applied, the script exits immediately with an exception before writing `docs/portfolio/latest-digest.md`, preventing a partial or corrupted report file from replacing the previous valid digest.
- **What data crosses a third party, and is any of it personal?**
  No data crosses any external third-party service—the script runs locally against `app.db` and writes to `docs/portfolio/latest-digest.md`. Furthermore, the digest only outputs aggregated counts (no user names, emails, or personal identifiers), so `latest-digest.md` contains zero personal data.