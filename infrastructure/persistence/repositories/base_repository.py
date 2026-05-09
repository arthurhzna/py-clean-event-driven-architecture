from __future__ import annotations


class BaseRepository:
    def __init__(
        self,
        uow,
    ) -> None:

        self._uow = uow

    @property
    def cursor(
        self,
    ):

        return self._uow.connection.cursor()