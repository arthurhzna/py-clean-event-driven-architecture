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

from infrastructure.config.device import (
    DeviceConfig,
    load_device_config,
)
from infrastructure.config.mqtt import (
    MQTTConfig,
    load_mqtt_config,
)


@dataclass
class Config:
    device: DeviceConfig
    database: DatabaseConfig
    http: HttpServerConfig
    mqtt: MQTTConfig
    jwt: JwtConfig
    logger: LoggerConfig


def load_config() -> Config:

    return Config(
        device=load_device_config(),
        database=load_database_config(),
        http=(load_http_server_config()),
        mqtt=load_mqtt_config(),
        jwt=load_jwt_config(),
        logger=load_logger_config(),
    )
