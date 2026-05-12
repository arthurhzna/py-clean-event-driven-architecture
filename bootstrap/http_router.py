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

from config.http import HttpServerConfig

from presentation.http.middleware.api_key_auth_middleware import (
    make_api_key_auth,
)


def register_http_routes(
    app: FastAPI,
    container: ApplicationContainer,
    http_config: HttpServerConfig,
) -> None:

    api_key_auth = make_api_key_auth(
        api_key=http_config.api_key,
    )

    app.include_router(
        make_device_router(
            register_device_factory=(
                lambda:
                    build_register_device_usecase(
                        container=container,
                    )
            ),
            api_key_auth=api_key_auth,
        ),
        prefix="/api/v1",
    )