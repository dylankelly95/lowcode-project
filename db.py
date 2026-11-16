import os
import sqlite3


def get_connection():
    """Open a SQLite connection with row access by column name and foreign keys enabled."""
    db_path = os.environ.get("DATABASE_PATH", "app.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# --- USERS ---

def create_user(email, full_name, username):
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO users (email, full_name, username) VALUES (?, ?, ?)",
            (email, full_name, username),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user(user_id):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()


def list_users():
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM users ORDER BY user_id ASC").fetchall()
    finally:
        conn.close()


def update_user(user_id, email, full_name, username):
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE users SET email = ?, full_name = ?, username = ? WHERE user_id = ?",
            (email, full_name, username, user_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_user(user_id):
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# --- ROLES ---

def create_role(role_name):
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO roles (role_name) VALUES (?)", (role_name,)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_role(role_id):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM roles WHERE role_id = ?", (role_id,)
        ).fetchone()
    finally:
        conn.close()


def list_roles():
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM roles ORDER BY role_id ASC").fetchall()
    finally:
        conn.close()


def update_role(role_id, role_name):
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE roles SET role_name = ? WHERE role_id = ?",
            (role_name, role_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_role(role_id):
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM roles WHERE role_id = ?", (role_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# --- USER ROLES ---

def assign_user_role(user_id, role_id):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)",
            (user_id, role_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_user_role(user_id, role_id):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM user_roles WHERE user_id = ? AND role_id = ?",
            (user_id, role_id),
        ).fetchone()
    finally:
        conn.close()


def list_user_roles(user_id=None):
    conn = get_connection()
    try:
        if user_id is not None:
            return conn.execute(
                """
                SELECT ur.user_id, ur.role_id, r.role_name
                FROM user_roles ur
                JOIN roles r ON ur.role_id = r.role_id
                WHERE ur.user_id = ?
                ORDER BY r.role_name ASC
                """,
                (user_id,),
            ).fetchall()
        return conn.execute(
            """
            SELECT ur.user_id, ur.role_id, u.username, r.role_name
            FROM user_roles ur
            JOIN users u ON ur.user_id = u.user_id
            JOIN roles r ON ur.role_id = r.role_id
            ORDER BY ur.user_id ASC, ur.role_id ASC
            """
        ).fetchall()
    finally:
        conn.close()


def update_user_role(user_id, old_role_id, new_role_id):
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE user_roles SET role_id = ? WHERE user_id = ? AND role_id = ?",
            (new_role_id, user_id, old_role_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def remove_user_role(user_id, role_id):
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM user_roles WHERE user_id = ? AND role_id = ?",
            (user_id, role_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# --- PORTFOLIOS ---

def create_portfolio(user_id, title, bio, theme=None):
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO portfolios (user_id, title, bio, theme) VALUES (?, ?, ?, ?)",
            (user_id, title, bio, theme),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_portfolio(portfolio_id):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM portfolios WHERE portfolio_id = ?", (portfolio_id,)
        ).fetchone()
    finally:
        conn.close()


def get_first_portfolio():
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM portfolios ORDER BY portfolio_id ASC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()


def list_portfolios():
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM portfolios ORDER BY portfolio_id ASC"
        ).fetchall()
    finally:
        conn.close()


def update_portfolio(portfolio_id, title, bio, theme=None):
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE portfolios SET title = ?, bio = ?, theme = ? WHERE portfolio_id = ?",
            (title, bio, theme, portfolio_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_portfolio(portfolio_id):
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM portfolios WHERE portfolio_id = ?", (portfolio_id,)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# --- PROJECTS ---

def create_project(portfolio_id, title, description, category_medium, release_date=None):
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO projects (portfolio_id, title, description, category_medium, release_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (portfolio_id, title, description, category_medium, release_date),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_project(project_id):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT *, project_id AS id FROM projects WHERE project_id = ?",
            (project_id,),
        ).fetchone()
    finally:
        conn.close()


def list_projects():
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT *, project_id AS id FROM projects ORDER BY project_id DESC"
        ).fetchall()
    finally:
        conn.close()


def update_project(project_id, portfolio_id, title, description, category_medium, release_date=None):
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            UPDATE projects
            SET portfolio_id = ?, title = ?, description = ?, category_medium = ?, release_date = ?
            WHERE project_id = ?
            """,
            (portfolio_id, title, description, category_medium, release_date, project_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_project(project_id):
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM projects WHERE project_id = ?", (project_id,)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# --- MEDIA ---

def create_media(project_id, file_name, file_type, file_url):
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO media (project_id, file_name, file_type, file_url)
            VALUES (?, ?, ?, ?)
            """,
            (project_id, file_name, file_type, file_url),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_media(media_id):
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT m.*, m.media_id AS id, p.title AS project_title
            FROM media m
            LEFT JOIN projects p ON m.project_id = p.project_id
            WHERE m.media_id = ?
            """,
            (media_id,),
        ).fetchone()
    finally:
        conn.close()


def list_media(project_id=None):
    conn = get_connection()
    try:
        if project_id is not None:
            return conn.execute(
                """
                SELECT m.*, m.media_id AS id, p.title AS project_title
                FROM media m
                LEFT JOIN projects p ON m.project_id = p.project_id
                WHERE m.project_id = ?
                ORDER BY m.media_id DESC
                """,
                (project_id,),
            ).fetchall()
        return conn.execute(
            """
            SELECT m.*, m.media_id AS id, p.title AS project_title
            FROM media m
            LEFT JOIN projects p ON m.project_id = p.project_id
            ORDER BY m.media_id DESC
            """
        ).fetchall()
    finally:
        conn.close()


def update_media(media_id, project_id, file_name, file_type, file_url):
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            UPDATE media
            SET project_id = ?, file_name = ?, file_type = ?, file_url = ?
            WHERE media_id = ?
            """,
            (project_id, file_name, file_type, file_url, media_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_media(media_id):
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM media WHERE media_id = ?", (media_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()