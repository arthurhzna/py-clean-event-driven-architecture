from abc import (
    ABC,
    abstractmethod,
)

from domain.entities.device import (
    Device,
)


class DeviceRepository(ABC):

    @abstractmethod
    def save(
        self,
        device: Device,
    ) -> None:
        pass

    @abstractmethod
    def get_by_id(
        self,
        device_id: str,
    ) -> Device | None:
        pass

    @abstractmethod
    def exists(
        self,
        device_id: str,
    ) -> bool:
        pass

    @abstractmethod
    def delete(
        self,
        device_id: str,
    ) -> None:
        pass
