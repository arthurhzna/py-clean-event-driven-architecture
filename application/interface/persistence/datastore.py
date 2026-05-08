from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import (
    Callable,
)
from typing import (
    Any,
)

from domain.interface.persistence.tx import (
    Tx,
)


class DataStore(ABC):
    @abstractmethod
    def atomic(
        self,
        fn: Callable[[Tx], Any],
    ) -> Any:
        pass

    @abstractmethod
    def query(
        self,
        fn: Callable[[Tx], Any],
    ) -> Any:
        pass
