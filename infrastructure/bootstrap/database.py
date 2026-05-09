from psycopg2.pool import (
    ThreadedConnectionPool,
)

from infrastructure.config.database import (
    DatabaseConfig,
)

from infrastructure.persistence.database.database import (
    Database,
)


def init_database(
    config: DatabaseConfig,
) -> ThreadedConnectionPool:

    db = Database(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
        min_conn=config.min_conn,
        max_conn=config.max_conn,
    )

    db.migrate()

    return db.connect()