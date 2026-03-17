from __future__ import annotations

import sqlite3
import ssl
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator, Optional
from urllib.parse import unquote, urlparse

import pg8000.dbapi as pg_dbapi

from .config import settings


def using_postgres() -> bool:
    url = settings.database_url
    return url.startswith(("postgres://", "postgresql://"))


def _postgres_connect():
    parsed = urlparse(settings.database_url)
    return pg_dbapi.connect(
        user=unquote(parsed.username or ""),
        password=unquote(parsed.password or ""),
        host=parsed.hostname or "localhost",
        port=parsed.port or 5432,
        database=(parsed.path or "/").lstrip("/"),
        ssl_context=ssl.create_default_context(),
    )


def _sqlite_connect():
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def connect() -> Iterator[Any]:
    connection = _postgres_connect() if using_postgres() else _sqlite_connect()
    try:
        yield connection
    finally:
        connection.close()


def _adapt_query(query: str) -> str:
    return query.replace("?", "%s") if using_postgres() else query


def fetch_one(query: str, params: tuple[Any, ...] = ()) -> Optional[dict[str, Any]]:
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(_adapt_query(query), params)
        row = cursor.fetchone()
        if row is None:
            return None
        return _row_to_dict(cursor, row)


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(_adapt_query(query), params)
        return [_row_to_dict(cursor, row) for row in cursor.fetchall()]


def execute(query: str, params: tuple[Any, ...] = ()) -> None:
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(_adapt_query(query), params)
        connection.commit()


def execute_returning_id(query: str, params: tuple[Any, ...] = ()) -> int:
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(_adapt_query(query), params)
        if using_postgres():
            row = cursor.fetchone()
            connection.commit()
            return int(row[0])
        connection.commit()
        return int(getattr(cursor, "lastrowid", 0))


def _row_to_dict(cursor: Any, row: Any) -> dict[str, Any]:
    if isinstance(row, sqlite3.Row):
        return dict(row)
    columns = [column[0] for column in cursor.description or []]
    return dict(zip(columns, row))


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db() -> None:
    if using_postgres():
        statements = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS auth_tokens (
                token_hash TEXT PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS password_resets (
                email TEXT NOT NULL REFERENCES users(email) ON DELETE CASCADE,
                reset_code TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (email, reset_code)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS resume_submissions (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
                submitted_by TEXT NOT NULL,
                resume_file TEXT,
                applied_role TEXT NOT NULL,
                match_score DOUBLE PRECISION NOT NULL,
                ats_score DOUBLE PRECISION NOT NULL,
                candidate_name TEXT,
                candidate_email TEXT,
                candidate_phone TEXT,
                skills TEXT,
                education TEXT,
                experience TEXT,
                extracted_text TEXT,
                ai_summary TEXT,
                ai_strengths TEXT,
                ai_risks TEXT,
                ai_next_steps TEXT,
                submitted_at TEXT NOT NULL
            )
            """,
        ]
    else:
        statements = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS auth_tokens (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS password_resets (
                email TEXT NOT NULL,
                reset_code TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (email, reset_code),
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS resume_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                submitted_by TEXT NOT NULL,
                resume_file TEXT,
                applied_role TEXT NOT NULL,
                match_score REAL NOT NULL,
                ats_score REAL NOT NULL,
                candidate_name TEXT,
                candidate_email TEXT,
                candidate_phone TEXT,
                skills TEXT,
                education TEXT,
                experience TEXT,
                extracted_text TEXT,
                ai_summary TEXT,
                ai_strengths TEXT,
                ai_risks TEXT,
                ai_next_steps TEXT,
                submitted_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """,
        ]

    with connect() as connection:
        cursor = connection.cursor()
        for statement in statements:
            cursor.execute(_adapt_query(statement))
        connection.commit()
