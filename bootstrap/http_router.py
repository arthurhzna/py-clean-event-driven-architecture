from __future__ import annotations

from fastapi import FastAPI

from bootstrap.container import (
    ApplicationContainer,
)

from bootstrap.usecase_factories.scoped_factories import (
    build_register_device_usecase,
)

from presentation.http.routes.device_routes import (
    make_device_router,
)


def register_http_routes(
    app: FastAPI,
    container: ApplicationContainer,
) -> None:

    app.include_router(
        make_device_router(
            lambda:
                build_register_device_usecase(
                    container=container,
                )
        ),
        prefix="/api/v1",
    )