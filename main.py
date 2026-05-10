from threading import Thread

import uvicorn

from bootstrap.application import (
    build_application,
)

application = build_application()

Thread(
    target=(
        application.device_runtime_runner.run
    ),
    daemon=True,
).start()

uvicorn.run(
    **application.uvicorn_config,
)