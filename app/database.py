from __future__ import annotations

import os
import sqlite3
from pathlib import Path


DATABASE_ENV_VAR = "COURSE_INFO_DATABASE"
DEFAULT_DATABASE_PATH = "./courses.db"
SQL_FILE = "./db_init.sql"


def get_database_path() -> str:
    return os.getenv(DATABASE_ENV_VAR, DEFAULT_DATABASE_PATH)


def connect(db_path: str | None = None) -> sqlite3.Connection:
    path = db_path or get_database_path()
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database(db_path: str | None = None) -> None:
    sql = Path(SQL_FILE).read_text()
    with connect(db_path) as connection:
        connection.executescript(sql)
