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
    ) -> None:

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

        self.url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def connect(
        self,
    ) -> ThreadedConnectionPool:

        return ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
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
