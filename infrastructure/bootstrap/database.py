from infrastructure.config.database import (
    DatabaseConfig,
)
from infrastructure.persistence.database.database import (
    Database,
)
from infrastructure.persistence.database.datastore import (
    DataStore,
)


def init_database(
    config: DatabaseConfig,
) -> DataStore:

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

    pool = db.connect()

    return DataStore(
        pool=pool,
    )
