from __future__ import annotations

import os
from dataclasses import (
    dataclass,
)


@dataclass
class HttpServerConfig:
    host: str
    port: int
    grace_period: int
    request_timeout_period: int


def load_http_server_config() -> HttpServerConfig:

    return HttpServerConfig(
        host=os.getenv(
            "HTTP_SERVER_HOST",
            "0.0.0.0",
        ),
        port=int(
            os.getenv(
                "HTTP_SERVER_PORT",
                "8000",
            )
        ),
        grace_period=int(
            os.getenv(
                "HTTP_SERVER_GRACE_PERIOD",
                "10",
            )
        ),
        request_timeout_period=int(
            os.getenv(
                "HTTP_SERVER_REQUEST_TIMEOUT_PERIOD",
                "30",
            )
        ),
    )
