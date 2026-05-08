from infrastructure.persistence.database.database import (
    Database,
)
from infrastructure.persistence.database.datastore import (
    DataStore,
)


def init_database() -> DataStore:

    db = Database(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="mydb",
    )

    db.migrate()

    pool = db.connect()

    return DataStore(
        pool=pool,
    )
