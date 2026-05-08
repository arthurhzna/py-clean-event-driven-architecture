import json

class RegisterDeviceMessageHandler:

    def __init__(
        self,
        register_device_usecase,
    ):

        self.register_device_usecase = (
            register_device_usecase
        )

    def __call__(
        self,
        payload: bytes,
    ) -> None:

        data = json.loads(payload)

        device_id = data["device_id"]

        self.register_device_usecase.execute(
            device_id=device_id
        )