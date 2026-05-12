from __future__ import annotations

from domain.entities.device import (
    Device,
)

from application.interfaces.persistence.repositories.device_repository import (
    DeviceRepository,
)

from infrastructure.persistence.repositories.base_repository import (
    BaseRepository,
)


class PostgresDeviceRepository(
    BaseRepository,
    DeviceRepository,
):

    def save(
        self,
        device: Device,
    ) -> None:

        with (
            self._uow.connection.cursor()
            as cur
        ):

            cur.execute(
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
        device_id: str,
    ) -> Device | None:

        with (
            self._uow.connection.cursor()
            as cur
        ):

            cur.execute(
                """
                SELECT
                    device_id,
                    is_registered
                FROM device
                WHERE device_id = %s
                """,
                (device_id,),
            )

            row = cur.fetchone()

            if row is None:
                return None

            return Device(
                device_id=row[0],
                is_registered=row[1],
            )

    def exists(
        self,
        device_id: str,
    ) -> bool:

        with (
            self._uow.connection.cursor()
            as cur
        ):

            cur.execute(
                """
                SELECT 1
                FROM device
                WHERE device_id = %s
                """,
                (device_id,),
            )

            return (
                cur.fetchone()
                is not None
            )

    def delete(
        self,
        device_id: str,
    ) -> None:

        with (
            self._uow.connection.cursor()
            as cur
        ):

            cur.execute(
                """
                DELETE FROM device
                WHERE device_id = %s
                """,
                (device_id,),
            )