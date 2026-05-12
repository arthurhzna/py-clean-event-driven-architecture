from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import APIRouter
from fastapi import Depends

from application.usecase.register_device_usecase import (
    RegisterDeviceUseCase,
)

from presentation.http.controllers.register_device_controller import (
    RegisterDeviceController,
)

from presentation.http.requests.register_device_request import (
    RegisterDeviceRequest,
)


def make_device_router(
    register_device_factory: Callable[
        [],
        RegisterDeviceUseCase,
    ],
    api_key_auth: Callable[..., Any],
) -> APIRouter:

    router = APIRouter(
        prefix="/devices",
        tags=["devices"],
    )

    @router.post(
        "/register",
        dependencies=[
            Depends(api_key_auth),
        ],
    )
    async def register_device(
        body: RegisterDeviceRequest,
    ):

        controller = (
            RegisterDeviceController(
                usecase_factory=(
                    register_device_factory
                ),
            )
        )

        return await controller.handle(
            body,
        )

    return router