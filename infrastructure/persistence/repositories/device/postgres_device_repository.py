from domain.entities.device import (
    Device,
)
from domain.interface.persistence.tx import (
    Tx,
)
from domain.interface.repositories.device_repository import (
    DeviceRepository,
)


class PostgresDeviceRepository(
    DeviceRepository,
):
    def save(
        self,
        tx: Tx,
        device: Device,
    ) -> None:

        tx.execute(
            """
            INSERT INTO device (
                device_id,
                is_registered
            )
            VALUES (%s, %s)

            ON CONFLICT (device_id)
            DO UPDATE SET
                is_registered = EXCLUDED.is_registered
            """,
            (
                device.device_id,
                device.is_registered,
            ),
        )

    def get_by_id(
        self,
        tx: Tx,
        device_id: int,
    ) -> Device | None:

        tx.execute(
            """
            SELECT
                device_id,
                is_registered
            FROM device
            WHERE device_id = %s
            """,
            (device_id,),
        )

        row = tx.fetchone()

        if row is None:
            return None

        return Device(
            device_id=row[0],
            is_registered=row[1],
        )

    def exists(
        self,
        tx: Tx,
        device_id: int,
    ) -> bool:

        tx.execute(
            """
            SELECT 1
            FROM device
            WHERE device_id = %s
            """,
            (device_id,),
        )

        return tx.fetchone() is not None

    def delete(
        self,
        tx: Tx,
        device_id: int,
    ) -> None:

        tx.execute(
            """
            DELETE FROM device
            WHERE device_id = %s
            """,
            (device_id,),
        )
