from __future__ import annotations

from fastapi import FastAPI

from bootstrap.container import ApplicationContainer
from config.http import HttpServerConfig
from presentation.http.exception_handlers.global_exception_handler import global_exception_handler
from presentation.http.middleware.api_key_middleware import ApiKeyMiddleware
from bootstrap.http_router import register_http_routes


def build_fastapi_app(
    container: ApplicationContainer,
    http_config: HttpServerConfig,
) -> FastAPI:

    app = FastAPI()

    app.add_exception_handler(
        Exception,
        global_exception_handler,
    )

    app.add_middleware(
        ApiKeyMiddleware,
        api_key=http_config.api_key,
    )

    register_http_routes(
        app=app,
        container=container,
    )

    return app


def build_uvicorn_config(
    app: FastAPI,
    http_config: HttpServerConfig,
) -> dict:

    return {
        "app": app,
        "host": http_config.host,
        "port": http_config.port,
        "timeout_graceful_shutdown": http_config.grace_period,
        "timeout_keep_alive": http_config.request_timeout_period,
    }