# AI-usage log: Artfolio

This log is a graded part of CA2. It feeds the AI Fluency declaration (Delegation, Description, Discernment, Diligence). Add an entry every time AI does something meaningful for your project, including the times it got things wrong. Paste prompts **exactly** as you typed them.

## Tools I used

| Tool | Version or plan | What I used it for |
|---|---|---|
| Gemini | 3.6 Flash | Initial SQL schema generation, `db.py` data layer, `app.py` wiring, `tests/test_constraints.py`, and unspecified AI decision audit |

## Log entries

---

### Entry 1: Generate the initial schema

- **Date:** 2026-11-11
- **Tool:** Gemini, 3.6 Flash
- **Task (why I used AI here):** For the lab in week 5 we were tasked to give our app a memory using AI. Rather than letting the AI invent the database structure or guess business rules, I constrained it to act strictly as a translator—implementing my exact tables, constraints and chosen delete rules and required it to explain each constraint in plain English and flag any unspecified design choices so I could audit the SQL line by line.
- **Prompt (verbatim):**

  ```text
  Read docs/data-model.md and AGENTS.md.

  Create ONE file, schema/001_initial.sql, that builds exactly the tables, fields and rules in
  docs/data-model.md, using SQLite syntax.
  - Do not change any other file.
  - Do not add tables or fields I did not list.
  - Use the delete rule I wrote in docs/data-model.md. If it is missing, STOP and ask me.
  - Store dates as TEXT in YYYY-MM-DD form.
  - Put a short comment on each line that has a rule (NOT NULL, UNIQUE, CHECK, REFERENCES).

  After the file, explain each constraint in one line of plain English.
  Then list any decision you made that I did not specify.
  ```

- **What it produced:** Created `schema/001_initial.sql` containing the SQLite DDL for all six tables (`users`, `roles`, `user_roles`, `portfolios`, `projects`, `media`) with all specified constraints and delete rules, along with plain-English constraint explanations and a list of unspecified decisions.
- **Decision:** Accepted
- **Why:** The generated SQL accurately translated every table, field, data type (`INTEGER` and `TEXT`), constraint (`NOT NULL`, `UNIQUE`, `CHECK`, `REFERENCES`), and chosen `ON DELETE` rule (`CASCADE` and `RESTRICT`) from `docs/data-model.md` without adding extra tables or altering my design.
- **What I checked:** Read `schema/001_initial.sql` field by field against `docs/data-model.md` using the Step 5 checklist (verifying SQLite syntax, primary keys, foreign keys, `CHECK` constraints, `TEXT` dates, and delete rules) and reviewed the AI's unspecified design choices (such as the composite primary key on `user_roles`).
- **Decisions the AI made that I did not specify:**
  - Composite Primary Key on `user_roles`: Defined `PRIMARY KEY (user_id, role_id)` so SQLite prevents duplicate `(user_id, role_id)` pairs and gives the junction table a valid primary key.
  - `NOT NULL` on `user_roles` Foreign Keys: Explicitly added `NOT NULL` alongside `REFERENCES` on `user_roles.user_id` and `user_roles.role_id` to match the "Required: yes" column in the data model.
  - Omitted `PRAGMA foreign_keys = ON` inside the migration file: Per `AGENTS.md` Rule 3, foreign-key enforcement is a per-connection runtime setting rather than a schema DDL statement, so it was left out of `schema/001_initial.sql`.
  - No `CHECK` format constraint on `projects.release_date`: Specified as optional `TEXT` (`YYYY-MM-DD`) without a formal `CHECK` expression, so no regex/date format `CHECK` constraint was added.
- **Commit:** `Add initial schema from data model` (`001_initial.sql` applied via `tools/migrate.py app.db`)

---

### Entry 2: Create the database layer and wire it to the Flask app

- **Date:** 2026-11-16
- **Tool:** Gemini, 3.6 Flash
- **Task (why I used AI here):** Generating `db.py` with parameterized CRUD functions for all six tables and updating `app.py` to persist data to `app.db` instead of in-memory lists, while handling missing records (`404`) and constraint violations (`sqlite3.IntegrityError`) gracefully.
- **Prompt (verbatim):**

  ```text
  Read AGENTS.md, docs/data-model.md, schema/ and app.py.

  1. Create db.py with:
     - a get_connection() function that opens app.db, sets row_factory = sqlite3.Row,
       and executes PRAGMA foreign_keys = ON on every connection
     - parameterised CRUD functions (? placeholders, never f-strings or +) for every table
  2. Update app.py to read and write through db.py instead of in-memory data:
     - a missing id returns 404, not a crash
     - a database rule error (sqlite3.IntegrityError) shows a helpful message, not a stack trace
     - no secrets in code

  Do not change the schema or any table/field names.
  Tell me the exact command to run my app on Mac.
  Then list any decision you made that I did not specify.
  ```

- **What it produced:** Created `db.py` with `get_connection()` (enforcing `PRAGMA foreign_keys = ON` and `sqlite3.Row`) and parameterized CRUD helpers for `users`, `roles`, `user_roles`, `portfolios`, `projects`, and `media`, and updated `app.py` to read/write through `db.py` with `404` and `IntegrityError` handling.
- **Decision:** Accepted
- **Why:** All SQL queries use `?` placeholders without string concatenation, `schema/001_initial.sql` was left untouched, secrets were kept out of source code via `os.environ.get("SECRET_KEY", os.urandom(24))`, and the app persisted records across server restarts.
- **What I checked:** Started the app (`python3 app.py`), created a record in the browser, stopped and restarted the server (`Ctrl + C`), and verified the record persisted in `app.db`. Ran `python3 tools/check_db.py app.db --src .` and confirmed zero `✗` errors (`Nothing to fix`), zero orphan rows, and `PRAGMA foreign_keys = ON` detected in `db.py:10`.
- **Decisions the AI made that I did not specify:**
  - Mapped `/work` routes in `app.py` to the `media` table and accepted fallback form field names (`title`, `media_type`, `media_url`) so existing templates stayed working.
  - Removed `/work/<int:work_id>/feature` because `media` has no `is_featured` column in `schema/001_initial.sql`.
  - Defaulted `category_medium` to `"General"` in `create_project()` when omitted from the old project form.
  - Added `AS id` aliases in `db.py` `SELECT` queries for `projects` and `media` to match `.id` references in existing Jinja templates.
  - Removed `init_db()` and `portfolio.db` from `app.py` so migrations are managed solely via `tools/migrate.py` on `app.db`.
- **Commit:** `Wire db.py data layer to app.py`

---

### Entry 3: Write automated database constraint and persistence tests

- **Date:** 2026-11-16
- **Tool:** Gemini, 3.6 Flash
- **Task (why I used AI here):** Writing an automated `unittest` suite in `tests/test_constraints.py` that builds a fresh temporary database from `schema/*.sql` for each test and verifies that invalid data is rejected by `UNIQUE`, `CHECK`, `NOT NULL`, `FOREIGN KEY`, and `ON DELETE` rules without touching `app.db`.
- **Prompt (verbatim):**

  ```text
  Read AGENTS.md, docs/data-model.md, schema/ and db.py.

  Write tests in tests/test_constraints.py using Python's built-in unittest (they must also run
  with pytest). Each test must create a fresh temporary database by running the files in
  schema/ in number order, and must never touch app.db.

  Write one test for EACH of these, each one trying to put BAD data in and checking it is REJECTED:
  - a duplicate value in a UNIQUE field
  - a value that breaks a CHECK rule
  - a missing value in a required (NOT NULL) field
  - a row pointing at a project (or portfolio / user) that does not exist (foreign key), using db.get_connection()
  - my delete rule: RESTRICT on portfolios -> projects (deleting a portfolio with projects is blocked) and CASCADE on users -> portfolios and projects -> media (the children are deleted too)
  Also write:
  - one test that saves a record, closes the connection, opens the file again and finds it
  - one test that asking for an id that does not exist returns None (not an error)

  Do not change my app, db.py or the schema to make a test pass. If a test fails, tell me why.
  Tell me the exact command to run the tests on Mac.
  Then list any decision you made that I did not specify.
  ```

- **What it produced:** Created `tests/__init__.py` and `tests/test_constraints.py` containing 8 automated tests covering `UNIQUE`, `CHECK`, `NOT NULL`, `FOREIGN KEY` (`PRAGMA foreign_keys = ON`), `RESTRICT` and `CASCADE` delete rules, persistence across connection close/reopen, and `None` return values for missing IDs.
- **Decision:** Accepted
- **Why:** All 8 tests run against isolated temporary SQLite files via `tempfile` and `DATABASE_PATH` without modifying `app.py`, `db.py`, `schema/001_initial.sql`, or `app.db`.
- **What I checked:** Ran `python3 -m unittest -v` in the terminal and confirmed all 8 tests executed and passed (`Ran 8 tests in 0.037s — OK`).
- **Decisions the AI made that I did not specify:**
  - Created an empty `tests/__init__.py` file so `python3 -m unittest -v` discovers the `tests` package automatically.
  - Used `tempfile.NamedTemporaryFile` + `DATABASE_PATH` in `setUp`/`tearDown` to isolate every test from `app.db` and clean up temporary `.db` files afterward.
  - Wrote separate tests for both `RESTRICT` (`portfolios -> projects`) and `CASCADE` (`projects -> media`) delete rules.
- **Commit:** `Add constraint tests (UNIQUE, CHECK, NOT NULL, FK, delete rule, persistence)`

---

### Entry 4: Audit all unspecified AI decisions from data layer work

- **Date:** 2026-11-16
- **Tool:** Gemini, 3.6 Flash
- **Task (why I used AI here):** Reviewing every assumption, fallback, naming choice, and structural change the AI made across `db.py`, `app.py`, and `tests/test_constraints.py` so I could explicitly decide whether to keep, change, or reject each one.
- **Prompt (verbatim):**

  ```text
  Do not change any files. Look back over everything you have done in this conversation and
  in this project today.

  List every decision you made that I did not explicitly specify. Include names you chose,
  data types, limits, default values, delete behaviour (ON DELETE), error handling, libraries,
  file locations, and anything you removed or rewrote.

  Give me a table with these columns:
  | Decision | What you chose | What else you could have chosen | Why you chose it | Risk if it is wrong |

  Then tell me which ONE of these decisions you think I should check first, and why.
  ```

- **What it produced:** A 10-row audit table covering every unspecified decision across `db.py`, `app.py`, and `tests/test_constraints.py`, plus a recommendation to inspect the `"General"` `category_medium` fallback and Week 3 HTML form inputs first.
- **Decision:** Accepted (audited each row individually below)
- **Why:** No files were modified, and the audit surfaced every hidden assumption—specifically highlighting that `templates/project_form.html` still lacks a `category_medium` input field, which I noted for the upcoming UI update.
- **What I checked:** Reviewed every row of the table against `docs/data-model.md`, `AGENTS.md`, `app.py`, `db.py`, and `tests/test_constraints.py`, and recorded my `Keep / Change / Reject` decision and rationale for each item.
- **Decisions the AI made that I did not specify:**

| Decision | What you chose | What else you could have chosen | Why you chose it | Risk if it is wrong | My decision & reason |
|---|---|---|---|---|---|
| **Mapped `/work` routes to the `media` table** | Wired `/work`, `/work/new`, and `/work/<id>` in `app.py` to query and insert into the `media` table instead of `work_items`. | Created separate `/media` routes, deleted `/work` routes, or asked you to rename the routes/templates first. | Your Week 3 `app.py` and HTML templates already used `/work` URLs, while `schema/001_initial.sql` replaced `work_items` with `media`. | Users or tests expecting `/media` endpoints won't find them, or the UI label ("Work Items") may feel slightly out of sync with the database table name (`media`). | **Keep** — Preserves all existing Week 3 URLs and Jinja templates without breaking navigation while saving records into the new `media` table. |
| **Accepted both old and new form field names in `create_work()`** | Read `file_name` (or fallback `title`), `file_type` (or fallback `media_type`), and `file_url` (or fallback `media_url`) from `request.form`. | Required only the new schema names (`file_name`, `file_type`, `file_url`) or edited `templates/work_form.html` directly. | Kept your existing `templates/work_form.html` working without touching template files you didn't ask to change. | If `work_form.html` is updated later with mismatched input names, old fallback names could mask a typo instead of failing clearly. | **Keep** — Allows `templates/work_form.html` to submit cleanly right now without altering HTML templates outside the data-layer scope; I can update the template field names in a later UI pass. |
| **Removed `/work/<int:work_id>/feature` (`toggle_feature`)** | Deleted the `toggle_feature` route and displayed the 6 most recent media rows (`db.list_media()[:6]`) as `featured_work` on `index()`. | Added an `is_featured` column via a `002_*.sql` migration or kept a stub route returning `404`. | `schema/001_initial.sql` has no `is_featured` column on `media`, and Prompt 03 forbade changing tables. | Clicking a "Feature" button in an older template (`work_detail.html`) will now return a `404 Not Found` error. | **Keep** — Matches my locked `docs/data-model.md` schema (which has no `is_featured` column) without inventing unrequested schema fields. |
| **Defaulted `category_medium` to `"General"` when omitted** | Used `request.form.get("category_medium", "").strip() or "General"` in `create_project()`. | Returned a `400` validation error requiring `category_medium` or added a dropdown to `templates/project_form.html`. | `projects.category_medium` is `NOT NULL` in `001_initial.sql`, and defaulting prevented your existing `project_form.html` from failing on submit. | Every project created via the old form gets labeled `"General"` instead of a real artistic medium unless you add the field to `project_form.html`. | **Keep (for now) / Note for UI update** — Keeps existing project creation working without `NOT NULL` errors; I checked `project_form.html` and will add a `category_medium` input field in the next UI milestone. |
| **Added `AS id` SQL aliases on `projects` and `media` `SELECT` queries** | Returned `SELECT *, project_id AS id` in `db.get_project`/`list_projects` and `SELECT m.*, m.media_id AS id` in `db.get_media`/`list_media`. | Returned only the exact schema column names (`project_id`, `media_id`) and updated every Jinja template to match. | Your Week 3 templates reference `.id` (e.g., `project.id`), so aliasing preserved template compatibility without rewriting HTML files. | Code calling `dict(row)` sees duplicate ID keys (`project_id` and `id`), which could confuse downstream JSON exports or future refactors. | **Keep** — Cleanly bridges `project_id`/`media_id` in SQLite with `.id` attributes expected by existing Jinja templates without modifying the database schema. |
| **Fallback `SECRET_KEY` using `os.urandom(24)`** | Set `app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(24))`. | Raised a `KeyError` if `os.environ["SECRET_KEY"]` was missing, or required a `.env` loader library (`python-dotenv`). | Satisfied the "no secrets in code" rule in `AGENTS.md` while letting `python3 app.py` start immediately without extra terminal setup. | Session cookies and `flash()` messages invalidate every time the server restarts unless `SECRET_KEY` is set in the environment. | **Keep** — Prevents hardcoding secrets in Git while allowing local development to run immediately without extra environment setup. |
| **Removed `init_db()` and `portfolio.db` reference from `app.py`** | Deleted `init_db()` (which ran `schema.sql` against `portfolio.db`) and routed all database access through `db.get_connection()` (`app.db`). | Kept `init_db()` pointed at `schema/001_initial.sql`. | `AGENTS.md` specifies that schema migrations are managed strictly by `tools/migrate.py` on `app.db`. | Running `python3 app.py` on a brand-new machine without running `tools/migrate.py app.db` first will raise `sqlite3.OperationalError: no such table`. | **Keep** — Follows `AGENTS.md` rules so schema migrations are controlled solely by `tools/migrate.py` on `app.db`. |
| **Returned `bool` (`cur.rowcount > 0`) from `update_*` and `delete_*` functions** | Made `update_*` and `delete_*` functions in `db.py` return `True` if a row was affected and `False` otherwise. | Returned `None` or the raw `sqlite3.Cursor` object. | Gives routes and tests a clean way to check whether a record actually existed when updating or deleting. | Minimal risk, though callers expecting the affected row count as an `int` receive a `bool` instead. | **Keep** — Makes route handlers and unit tests readable and explicit when verifying whether an update or delete succeeded. |
| **Created `tests/__init__.py` and `tests/test_constraints.py` with `tempfile` isolation** | Added an empty `tests/__init__.py` so `python3 -m unittest -v` discovers the test module, and used `tempfile.NamedTemporaryFile` + `DATABASE_PATH` in `setUp`/`tearDown`. | Used `:memory:` SQLite databases or required `python3 -m unittest discover -s tests`. | Ensured `python3 -m unittest -v` works out of the box and proved file-level persistence across `close()` and reopen without touching `app.db`. | If `tearDown` is interrupted abnormally, a leftover `.db` file could remain in `/tmp`. | **Keep** — Guarantees `python3 -m unittest -v` discovers all tests automatically and isolates every test run from `app.db`. |
| **Tested both `RESTRICT` and `CASCADE` delete rules** | Wrote two delete-rule tests in `tests/test_constraints.py`: one for `RESTRICT` (`portfolios -> projects`) and one for `CASCADE` (`projects -> media`). | Tested only a single delete rule. | Your data model explicitly uses both rules (`RESTRICT` to protect projects, `CASCADE` to clean up media), so testing both proves the full design. | None — both tests pass and verify your exact rules. | **Keep** — Verifies both sides of my delete-rule design (`RESTRICT` on `portfolios -> projects` and `CASCADE` on `projects -> media`). |

- **Commit:** `Log AI decisions from data layer work`