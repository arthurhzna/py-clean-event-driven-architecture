from domain.interface.persistence.tx import (
    Tx as TxInterface,
)


class Tx(TxInterface):
    def __init__(
        self,
        conn,
    ) -> None:

        self._conn = conn

        self._cursor = conn.cursor()

    def execute(
        self,
        query: str,
        params=None,
    ) -> None:

        self._cursor.execute(
            query,
            params,
        )

    def fetchone(
        self,
    ):

        return self._cursor.fetchone()

    def fetchall(
        self,
    ):

        return self._cursor.fetchall()
