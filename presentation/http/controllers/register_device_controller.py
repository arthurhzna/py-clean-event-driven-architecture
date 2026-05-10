from __future__ import annotations

from collections.abc import Callable
from http import HTTPStatus

from application.dto.input.register_device_input import (
    RegisterDeviceInput,
)

from application.usecase.register_device_usecase import (
    RegisterDeviceUseCase,
)

from presentation.http.presenters.device_presenter import (
    DevicePresenter,
)

from presentation.http.requests.register_device_request import (
    RegisterDeviceRequest,
)

from presentation.http.responses.shared.response_helper import (
    ParamHTTPResp,
    http_response,
)


class RegisterDeviceController:
    def __init__(
        self,
        usecase_factory: Callable[
            [],
            RegisterDeviceUseCase,
        ],
    ) -> None:

        self._factory = (
            usecase_factory
        )

    async def handle(
        self,
        request: RegisterDeviceRequest,
    ):

        usecase = self._factory()

        input_dto = (
            RegisterDeviceInput(
                device_id=request.device_id,
            )
        )

        result = usecase.execute(
            input_dto,
        )

        if result.is_err():

            return http_response(
                ParamHTTPResp(
                    code=(
                        HTTPStatus
                        .BAD_REQUEST
                    ),
                    err=result.error,
                )
            )

        response = (
            DevicePresenter
            .to_response(
                result.value,
            )
        )

        return http_response(
            ParamHTTPResp(
                code=HTTPStatus.CREATED,
                data=response.model_dump(),
            )
        )