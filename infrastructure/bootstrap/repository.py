from infrastructure.persistence.repositories.device.postgres_device_repository import (
    PostgresDeviceRepository,
)


def build_device_repository() -> PostgresDeviceRepository:

    return PostgresDeviceRepository()
