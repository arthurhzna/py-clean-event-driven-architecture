from __future__ import annotations

from dataclasses import (
    dataclass,
)

from infrastructure.config.database import (
    DatabaseConfig,
    load_database_config,
)
from infrastructure.config.httpserver import (
    HttpServerConfig,
    load_http_server_config,
)
from infrastructure.config.jwt import (
    JwtConfig,
    load_jwt_config,
)
from infrastructure.config.logger import (
    LoggerConfig,
    load_logger_config,
)


@dataclass
class Config:
    database: DatabaseConfig
    http_server: HttpServerConfig
    jwt: JwtConfig
    logger: LoggerConfig


def load_config() -> Config:

    return Config(
        database=load_database_config(),
        http_server=(load_http_server_config()),
        jwt=load_jwt_config(),
        logger=load_logger_config(),
    )
