from abc import ABC, abstractmethod
from typing import Optional


class DeviceRepository(ABC):

    @abstractmethod
    def save(
        self,
        device_id: int,
    ) -> None:
        pass

    @abstractmethod
    def get_by_id(
        self,
        device_id: int,
    ) -> Optional[dict]:
        pass

    @abstractmethod
    def exists(
        self,
        device_id: int,
    ) -> bool:
        pass