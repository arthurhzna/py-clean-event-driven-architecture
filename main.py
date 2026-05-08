from threading import (
    Thread,
)

from infrastructure.bootstrap.application import (
    build_application,
)

app = build_application()

Thread(
    target=(app.device_runtime_runner.run),
    daemon=True,
).start()

while True:
    pass
