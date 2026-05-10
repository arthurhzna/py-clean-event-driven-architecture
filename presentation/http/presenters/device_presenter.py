from __future__ import annotations

from application.dto.output.register_device_output import (
    RegisterDeviceOutput,
)

from presentation.http.responses.register_device_response import (
    RegisterDeviceData,
)


class DevicePresenter:
    @staticmethod
    def to_response(
        output: RegisterDeviceOutput,
    ) -> RegisterDeviceData:

        return RegisterDeviceData(
            device_id=output.device_id,
            status=(
                "active"
                if output.is_registered
                else "inactive"
            ),
        )