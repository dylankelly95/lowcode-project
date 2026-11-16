import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import db


SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schema"


class TestDatabaseConstraints(unittest.TestCase):
    def setUp(self):
        """Create a fresh temporary SQLite database and apply all schema migrations in order."""
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = tmp.name
        tmp.close()

        self._old_db_path = os.environ.get("DATABASE_PATH")
        os.environ["DATABASE_PATH"] = self.db_path

        conn = db.get_connection()
        try:
            for sql_file in sorted(SCHEMA_DIR.glob("*.sql")):
                conn.executescript(sql_file.read_text(encoding="utf-8"))
            conn.commit()
        finally:
            conn.close()

    def tearDown(self):
        """Restore environment and remove the temporary database file."""
        if self._old_db_path is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = self._old_db_path

        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _seed_project(self):
        """Helper to insert a valid user -> portfolio -> project chain."""
        user_id = db.create_user("alex@example.com", "Alex Rivera", "arivera")
        portfolio_id = db.create_portfolio(
            user_id, "Alex Soundscapes", "Ambient artist", "dark"
        )
        project_id = db.create_project(
            portfolio_id, "Midnight Echoes", "Ambient synth track", "Music", "2026-03-01"
        )
        return user_id, portfolio_id, project_id

    def test_duplicate_unique_username_is_rejected(self):
        """Inserting a duplicate username must raise IntegrityError."""
        db.create_user("alex@example.com", "Alex Rivera", "arivera")
        with self.assertRaises(sqlite3.IntegrityError):
            db.create_user("other@example.com", "Alex Two", "arivera")

    def test_invalid_check_file_type_is_rejected(self):
        """Inserting a media file_type outside ('image', 'audio', 'video') must fail."""
        _, _, project_id = self._seed_project()
        with self.assertRaises(sqlite3.IntegrityError):
            db.create_media(
                project_id, "notes.pdf", "document", "https://example.com/notes.pdf"
            )

    def test_missing_not_null_field_is_rejected(self):
        """Inserting NULL into a required NOT NULL column must raise IntegrityError."""
        with self.assertRaises(sqlite3.IntegrityError):
            db.create_user("noname@example.com", None, "noname")

    def test_foreign_key_pointing_at_missing_parent_is_rejected(self):
        """Pointing media.project_id at a non-existent project (999) must fail with PRAGMA on."""
        with self.assertRaises(sqlite3.IntegrityError):
            db.create_media(
                999, "cover.png", "image", "https://example.com/cover.png"
            )

    def test_delete_rule_restrict_blocks_deleting_portfolio_with_projects(self):
        """RESTRICT: deleting a portfolio that still has projects must be blocked."""
        _, portfolio_id, _ = self._seed_project()
        with self.assertRaises(sqlite3.IntegrityError):
            db.delete_portfolio(portfolio_id)

    def test_delete_rule_cascade_deletes_media_when_project_deleted(self):
        """CASCADE: deleting a project automatically deletes its child media rows."""
        _, _, project_id = self._seed_project()
        media_id = db.create_media(
            project_id, "track01.mp3", "audio", "https://example.com/track01.mp3"
        )
        self.assertIsNotNone(db.get_media(media_id))

        deleted = db.delete_project(project_id)
        self.assertTrue(deleted)
        self.assertIsNone(db.get_media(media_id))

    def test_data_persists_after_closing_and_reopening_database(self):
        """Saving a record, closing the connection, and reopening the file finds the record."""
        user_id = db.create_user("persist@example.com", "Sam Chen", "schen")

        # Open a brand-new connection directly to the temporary database file
        reopened = sqlite3.connect(self.db_path)
        reopened.row_factory = sqlite3.Row
        try:
            row = reopened.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
        finally:
            reopened.close()

        self.assertIsNotNone(row)
        self.assertEqual(row["username"], "schen")
        self.assertEqual(row["email"], "persist@example.com")

    def test_get_nonexistent_id_returns_none(self):
        """Asking for an ID that does not exist returns None rather than raising an error."""
        self.assertIsNone(db.get_user(99999))
        self.assertIsNone(db.get_portfolio(99999))
        self.assertIsNone(db.get_project(99999))
        self.assertIsNone(db.get_media(99999))


if __name__ == "__main__":
    unittest.main()