from __future__ import annotations
import sqlite3
import logging
from app.core.paths import DATABASE_PATH

logger = logging.getLogger(__name__)

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT '',
                education TEXT NOT NULL DEFAULT 'B.Tech',
                branch TEXT NOT NULL DEFAULT 'Computer Science',
                cgpa REAL NOT NULL DEFAULT 8.0,
                skills TEXT NOT NULL DEFAULT '[]',
                interests TEXT NOT NULL DEFAULT '[]',
                career_goal TEXT NOT NULL DEFAULT 'Software Developer',
                hours_per_day REAL NOT NULL DEFAULT 2.0,
                days_per_week INTEGER NOT NULL DEFAULT 5,
                created_at TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT ''
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmap_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                career_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT DEFAULT NULL,
                notes TEXT DEFAULT '',
                UNIQUE(career_id, task_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER DEFAULT NULL,
                career_target TEXT NOT NULL DEFAULT '',
                resume_data TEXT NOT NULL DEFAULT '{}',
                updated_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (profile_id) REFERENCES student_profile(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        _migrate_schema(conn)
        logger.info("Database initialized successfully at %s", DATABASE_PATH)
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)
        conn.rollback()
        raise
    finally:
        conn.close()

def _migrate_schema(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    expected_profile_cols = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL DEFAULT ''",
        "email": "TEXT NOT NULL DEFAULT ''",
        "education": "TEXT NOT NULL DEFAULT 'B.Tech'",
        "branch": "TEXT NOT NULL DEFAULT 'Computer Science'",
        "cgpa": "REAL NOT NULL DEFAULT 8.0",
        "skills": "TEXT NOT NULL DEFAULT '[]'",
        "interests": "TEXT NOT NULL DEFAULT '[]'",
        "career_goal": "TEXT NOT NULL DEFAULT 'Software Developer'",
        "hours_per_day": "REAL NOT NULL DEFAULT 2.0",
        "days_per_week": "INTEGER NOT NULL DEFAULT 5",
        "created_at": "TEXT NOT NULL DEFAULT ''",
        "updated_at": "TEXT NOT NULL DEFAULT ''"
    }

    cursor.execute("PRAGMA table_info(student_profile)")
    existing_cols = {row["name"] for row in cursor.fetchall()}

    for col_name, col_def in expected_profile_cols.items():
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE student_profile ADD COLUMN {col_name} {col_def}")
            except sqlite3.OperationalError:
                pass

    conn.commit()
