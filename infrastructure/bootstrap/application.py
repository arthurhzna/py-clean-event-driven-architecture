from infrastructure.bootstrap.database import (
    init_database,
)
from infrastructure.bootstrap.repository import (
    build_device_repository,
)

db = init_database()

conn = db.get_conn()

device_repository = build_device_repository(
    conn=conn,
)
