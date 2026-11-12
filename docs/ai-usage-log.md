# AI-usage log: [YOUR APP NAME]

This log is a graded part of CA2. It feeds the AI Fluency declaration (Delegation, Description, Discernment, Diligence). Add an entry every time AI does something meaningful for your project, including the times it got things wrong. Paste prompts **exactly** as you typed them.

## Tools I used

| Tool | Version or plan | What I used it for |
|---|---|---|
| [e.g. Cursor / Claude Code / GitHub Copilot / Gemini / ChatGPT] | [free / paid / version] | [schema, data layer, tests ...] |

## Log entries

Copy the block below for each entry.

---

### Entry [N]: [short title]

- **Date:** [2026-11-11]
- **Tool:** [Gemini, 3.6 Flash]
- **Task (why I used AI here):** [For the lab in week 5 we were tasked to give our app a memory using AI. Rather than letting the AI invent the database structure or guess business rules, I constrained it to act strictly as a translator—implementing my exact tables, constraints and chosen delete rules and required it to explain each constraint in plain English and flag any unspecified design choices so I could audit the SQL line by line.]
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

- **What it produced:** Created `schema/001_initial.sql` containing the SQLite DDL for all six tables (`users`, `roles`, `user_roles`, `portfolios`, `projects`, `media`) with all specified constraints and delete rules, along with plain-English constraint explanations and a list of unspecified decisions
- **Decision:** Accepted
- **Why:** The generated SQL accurately translated every table, field, data type (`INTEGER` and `TEXT`), constraint (`NOT NULL`, `UNIQUE`, `CHECK`, `REFERENCES`), and chosen `ON DELETE` rule (`CASCADE` and `RESTRICT`) from `docs/data-model.md` without adding extra tables or altering my design.
- **What I checked:** Read `schema/001_initial.sql` field by field against `docs/data-model.md` using the Step 5 checklist (verifying SQLite syntax, primary keys, foreign keys, `CHECK` constraints, `TEXT` dates, and delete rules) and reviewed the AI's unspecified design choices (such as the composite primary key on `user_roles`).
- **Decisions the AI made that I did not specify:
-Composite Primary Key on user_roles: Your data model listed user_id and role_id as required foreign keys on user_roles without specifying a primary key. I defined PRIMARY KEY (user_id, role_id) so SQLite prevents duplicate (user_id, role_id) pairs and gives the junction table a valid primary key.   
-NOT NULL on user_roles Foreign Keys: Explicitly added NOT NULL alongside REFERENCES on user_roles.user_id and user_roles.role_id to match the "Required: yes" column in your data model.   
-Omitted PRAGMA foreign_keys = ON inside the migration file: Per AGENTS.md Rule 3, foreign-key enforcement is a per-connection runtime setting rather than a schema DDL statement, so it is left out of schema/001_initial.sql.   
-No CHECK format constraint on projects.release_date: Your data model specified release_date as optional TEXT (YYYY-MM-DD) without a formal CHECK expression, so no regex/date format CHECK constraint was added.
- **Commit:** [the commit message or hash where this landed]

---

## Worked example (from the club equipment loans demo in Session 5)

### Entry 2: Generate the initial schema

- **Date:** 2026-11-11
- **Tool:** Claude Code
- **Task (why I used AI here):** turning my finished `docs/data-model.md` into SQL. I had already decided the tables and the delete rule myself; typing CREATE TABLE statements is the kind of mechanical job AI is good at.
- **Prompt (verbatim):**

  ```text
  Read docs/data-model.md and AGENTS.md. Create ONE file, schema/001_initial.sql, that builds
  exactly the tables, fields and rules in docs/data-model.md, using SQLite syntax. Do not
  change any other file. Do not add tables or fields I did not list. After the file, explain
  each constraint in one line of plain English, then list any decision you made that I did
  not specify.
  ```

- **What it produced:** `schema/001_initial.sql` with three tables (member, equipment, loan).
- **Decision:** Modified
- **Why:** it wrote `ON DELETE CASCADE` on both foreign keys even though my data model says RESTRICT. Cascade would wipe a member's loan history if they left the club, and the committee needs that history for insurance. I changed both to `ON DELETE RESTRICT`. It also added `AUTOINCREMENT`, which SQLite does not need here; I left that in and noted it.
- **What I checked:** read the SQL field by field against my data model (checklist in the lab guide), ran `python tools/migrate.py app.db`, then tried three bad inserts with `tools/sql.py`. The orphan loan got in until I used `--fk`, which led to the PRAGMA rule in AGENTS.md.
- **Decisions the AI made that I did not specify:** CASCADE on both foreign keys (changed), AUTOINCREMENT on ids (kept), `DEFAULT (date('now'))` on borrowed_on (kept).
- **Commit:** `Add initial schema from data model (delete rule: RESTRICT)`

> The tool responses in this worked example are illustrative of what agents commonly do. Your log must describe what YOUR tool actually did.
