#!/usr/bin/env python3
"""
CA1 Automation #2: Artist Portfolio Database Digest
Reads app.db via db.get_connection() (with PRAGMA foreign_keys = ON) and generates
an aggregate summary report of artists, portfolios, projects, and attached media.
"""

from datetime import datetime
from pathlib import Path
import sys

# Allow importing db.py from the project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import db


def build_digest() -> str:
    """Query app.db and return a formatted aggregate Markdown summary report."""
    with db.get_connection() as conn:
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        portfolio_count = conn.execute("SELECT COUNT(*) FROM portfolios").fetchone()[0]
        project_count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        media_count = conn.execute("SELECT COUNT(*) FROM media").fetchone()[0]

        unscheduled_count = conn.execute(
            "SELECT COUNT(*) FROM projects WHERE release_date IS NULL OR release_date = ''"
        ).fetchone()[0]

        empty_projects_count = conn.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT p.project_id
                FROM projects p
                LEFT JOIN media m ON p.project_id = m.project_id
                GROUP BY p.project_id
                HAVING COUNT(m.media_id) = 0
            )
            """
        ).fetchone()[0]

        projects_by_medium = conn.execute(
            """
            SELECT category_medium, COUNT(*) AS total
            FROM projects
            GROUP BY category_medium
            ORDER BY total DESC, category_medium ASC
            """
        ).fetchall()

        media_by_type = conn.execute(
            """
            SELECT file_type, COUNT(*) AS total
            FROM media
            GROUP BY file_type
            ORDER BY total DESC, file_type ASC
            """
        ).fetchall()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Artfolio Platform Summary Digest ({timestamp})",
        "",
        "## Platform Totals",
        f"- **Artists (`users`):** {user_count}",
        f"- **Portfolios (`portfolios`):** {portfolio_count}",
        f"- **Projects (`projects`):** {project_count}",
        f"- **Media Assets (`media`):** {media_count}",
        "",
        "## Project Status Overview",
        f"- **Projects Missing a Release Date:** {unscheduled_count}",
        f"- **Projects With No Attached Media:** {empty_projects_count}",
        "",
        "## Projects by Creative Medium",
    ]

    if projects_by_medium:
        for row in projects_by_medium:
            lines.append(f"- **{row['category_medium']}:** {row['total']}")
    else:
        lines.append("- No projects created yet.")

    lines.extend(["", "## Media Breakdown by File Type"])

    if media_by_type:
        for row in media_by_type:
            lines.append(f"- **{row['file_type']}:** {row['total']}")
    else:
        lines.append("- No media items uploaded yet.")

    return "\n".join(lines) + "\n"


def main() -> None:
    report = build_digest()
    output_path = ROOT_DIR / "docs" / "portfolio" / "latest-digest.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"Saved digest report to: {output_path}")


if __name__ == "__main__":
    main()