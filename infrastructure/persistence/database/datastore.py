from collections.abc import (
    Callable,
)
from typing import (
    Any,
)

from application.interface.persistence.datastore import (
    DataStore as DataStoreInterface,
)
from domain.interface.persistence.tx import (
    Tx as TxInterface,
)
from infrastructure.persistence.database.tx import (
    Tx,
)


class DataStore(
    DataStoreInterface,
):
    def __init__(
        self,
        pool,
    ) -> None:
        self._pool = pool

    def query(
        self,
        fn: Callable[[TxInterface], Any],
    ) -> Any:
        conn = self._pool.getconn()

        try:
            tx = Tx(conn)
            return fn(tx)
        finally:
            self._pool.putconn(conn)

    def atomic(
        self,
        fn: Callable[[TxInterface], Any],
    ) -> Any:
        conn = self._pool.getconn()

        try:
            tx = Tx(conn)
            result = fn(tx)
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)
