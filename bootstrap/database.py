from psycopg2.pool import (
    ThreadedConnectionPool,
)

from config.database import (
    DatabaseConfig,
)

from infrastructure.persistence.database.database import (
    Database,
)


def init_database(
    db_config: DatabaseConfig,
) -> ThreadedConnectionPool:

    db = Database(
        host=db_config.host,
        port=db_config.port,
        user=db_config.user,
        password=db_config.password,
        database=db_config.database,
        min_conn=db_config.min_conn,
        max_conn=db_config.max_conn,
    )

    db.migrate()

    return db.connect()