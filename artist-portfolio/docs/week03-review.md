# Week 03 — AI Code Review Log

**Scope:** Review of `artist-portfolio/app.py` for correctness, structure, and database reliability.

---

## 1. Prioritized Findings Table

| Priority | Category | File & Line | Problem Description | Impact / Why it Matters |
| :--- | :--- | :--- | :--- | :--- |
| **Medium** | Correctness | `app.py:55-64` | Project description lacks a length limit. | Oversized input can fill storage or cause UI rendering issues. |
| **Medium** | Reliability | `app.py:26, 67` | Database queries use `LIMIT 1` without explicit `ORDER BY`. | SQLite does not guarantee which record is returned when multiple exist. |
| **Medium** | Correctness | `app.py:121-124` | Invalid non-numeric `project_id` converted to `None`. | Invalid inputs silently default to unassigned work items rather than raising validation errors. |
| **Low** | Structure | `app.py:10-13` | SQLite connections lack central exception/cleanup handling. | Exceptions between open and close calls can leak database connections. |

---

## 2. Selected Issues to Fix

We have selected **two practical, non-security fixes** to implement:

1. **Fix 1 — Project Description Length Validation (`app.py:55-64`):** Ensure project descriptions are capped at 500 characters before saving.
2. **Fix 2 — Explicit Query Ordering (`app.py:26, 67`):** Add `ORDER BY id ASC` to `LIMIT 1` portfolio queries to guarantee consistent record selection.

