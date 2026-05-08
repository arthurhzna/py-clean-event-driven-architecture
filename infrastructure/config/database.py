# infrastructure/config/database.py

from __future__ import annotations

import os
from dataclasses import (
    dataclass,
)


@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    min_conn: int
    max_conn: int


def load_database_config() -> DatabaseConfig:

    return DatabaseConfig(
        host=os.getenv(
            "DB_HOST",
            "localhost",
        ),
        port=int(
            os.getenv(
                "DB_PORT",
                "5432",
            )
        ),
        user=os.getenv(
            "DB_USER",
            "postgres",
        ),
        password=os.getenv(
            "DB_PASSWORD",
            "postgres",
        ),
        database=os.getenv(
            "DB_NAME",
            "mydb",
        ),
        min_conn=int(
            os.getenv(
                "DB_MIN_CONN",
                "2",
            )
        ),
        max_conn=int(
            os.getenv(
                "DB_MAX_CONN",
                "10",
            )
        ),
    )
