from __future__ import annotations

import os
from dataclasses import (
    dataclass,
)


@dataclass
class JwtConfig:
    allowed_algs: list[str]
    issuer: str
    secret_key: str
    token_duration: int


def load_jwt_config() -> JwtConfig:

    allowed_algs = os.getenv(
        "JWT_ALLOWED_ALGS",
        "HS256",
    )

    return JwtConfig(
        allowed_algs=[alg.strip() for alg in allowed_algs.split(",")],
        issuer=os.getenv(
            "JWT_ISSUER",
            "",
        ),
        secret_key=os.getenv(
            "JWT_SECRET_KEY",
            "",
        ),
        token_duration=int(
            os.getenv(
                "JWT_TOKEN_DURATION",
                "0",
            )
        ),
    )
