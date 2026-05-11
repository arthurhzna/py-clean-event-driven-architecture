from __future__ import annotations

from application.interfaces.persistence.unit_of_work import (
    UnitOfWork,
)


class PostgresUnitOfWork(
    UnitOfWork,
):
    def __init__(
        self,
        pool,
    ) -> None:
        self._pool = pool
        self._conn = None

    @property
    def connection(
        self,
    ):
        return self._conn

    def __enter__(
        self,
    ) -> PostgresUnitOfWork:

        self._conn = (
            self._pool.getconn()
        )
        return self

    def commit(
        self,
    ) -> None:
        self._conn.commit()

    def rollback(
        self,
    ) -> None:
        self._conn.rollback()

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        try:
            if exc_type:
                self.rollback()

            else:
                self.commit()

        except Exception:
            self.rollback()
            raise
        finally:
            if self._conn is not None:
                self._pool.putconn(
                    self._conn,
                )
                self._conn = None