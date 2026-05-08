from __future__ import annotations

import os
from dataclasses import (
    dataclass,
)


@dataclass
class LoggerConfig:
    level: int


def load_logger_config() -> LoggerConfig:

    return LoggerConfig(
        level=int(
            os.getenv(
                "LOGGER_LEVEL",
                "20",
            )
        ),
    )
