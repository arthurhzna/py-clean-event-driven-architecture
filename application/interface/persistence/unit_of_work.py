from abc import (
    ABC,
    abstractmethod,
)


class UnitOfWork(ABC):

    @abstractmethod
    def __enter__(
        self,
    ) -> "UnitOfWork":
        pass

    @abstractmethod
    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:
        pass

    @abstractmethod
    def commit(
        self,
    ) -> None:
        pass

    @abstractmethod
    def rollback(
        self,
    ) -> None:
        pass