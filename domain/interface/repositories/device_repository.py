from abc import (
    ABC,
    abstractmethod,
)

from domain.entities.device import (
    Device,
)
from domain.interface.database.tx import (
    Tx,
)


class DeviceRepository(ABC):
    @abstractmethod
    def save(
        self,
        tx: Tx,
        device: Device,
    ) -> None:
        pass

    @abstractmethod
    def get_by_id(
        self,
        tx: Tx,
        device_id: int,
    ) -> Device | None:
        pass

    @abstractmethod
    def exists(
        self,
        tx: Tx,
        device_id: int,
    ) -> bool:
        pass

    @abstractmethod
    def delete(
        self,
        tx: Tx,
        device_id: int,
    ) -> None:
        pass
