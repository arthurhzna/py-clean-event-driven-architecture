from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
)


class Tx(ABC):
    @abstractmethod
    def execute(
        self,
        query: str,
        params=None,
    ) -> None:
        pass

    @abstractmethod
    def fetchone(
        self,
    ) -> Any:
        pass

    @abstractmethod
    def fetchall(
        self,
    ) -> Any:
        pass
