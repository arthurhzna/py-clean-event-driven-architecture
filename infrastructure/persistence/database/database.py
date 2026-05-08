from __future__ import annotations

import os

from psycopg2.pool import (
    ThreadedConnectionPool,
)
from yoyo import (
    get_backend,
    read_migrations,
)


class Database:
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        min_conn: int = 2,
        max_conn: int = 10,
    ) -> None:

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

        self.min_conn = min_conn
        self.max_conn = max_conn

        self.url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def connect(
        self,
    ) -> ThreadedConnectionPool:

        return ThreadedConnectionPool(
            minconn=self.min_conn,
            maxconn=self.max_conn,
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )

    def migrate(
        self,
    ) -> None:

        migrations_path = os.path.join(
            os.path.dirname(__file__),
            "migrations",
        )

        backend = get_backend(
            self.url,
        )

        migrations = read_migrations(
            migrations_path,
        )

        with backend.lock():
            backend.apply_migrations(
                backend.to_apply(
                    migrations,
                ),
            )
