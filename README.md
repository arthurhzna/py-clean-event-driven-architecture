<p align="center">
  <img src="./architecture.svg" alt="Clean Architecture Diagram" width="420"/>
</p>

# Python Clean Event-Driven Architecture

A scalable and high-performance Python template built with a modular and maintainable architecture.

This template is designed to support a wide range of applications — from small services to large-scale systems — while maintaining clear boundaries, extensibility, and long-term maintainability.

## Architecture

Dependencies point inward. The domain stays independent from frameworks and infrastructure.

```text
Presentation   ->  Application  ->  Domain
Infrastructure ->  Application  ->  Domain
Bootstrap      ->  all layers (composition root)
```


| Layer             | Responsibility                                                   |
| ----------------- | ---------------------------------------------------------------- |
| `domain/`         | entities, domain events, domain errors, pure domain services     |
| `application/`    | use cases, DTOs, interfaces, result type, shared in-memory state |
| `infrastructure/` | PostgreSQL, MQTT client, event bus implementation, runners       |
| `presentation/`   | HTTP routes/controllers and inbound message handlers             |
| `bootstrap/`      | dependency wiring and application startup                        |


## Implemented Flows

### 1. HTTP device registration

```text
POST /api/v1/devices/register
  -> X-API-Key dependency
  -> RegisterDeviceController
  -> RegisterDeviceUseCase
  -> PostgresDeviceRepository + PostgresUnitOfWork
  -> StateManager.update_device_publish_permission(True)
  -> HTTP response envelope
```

Request:

```bash
curl -X POST http://localhost:8000/api/v1/devices/register \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: your-api-key' \
  -d '{"device_id":"PC_GAMINGKU"}'
```

Success response:

```json
{
  "status": "success",
  "message": "Created",
  "data": {
    "device_id": "PC_GAMINGKU",
    "status": "active"
  }
}
```

If the device already exists, the use case returns `Err(DeviceError.DEVICE_ALREADY_REGISTERED)` and the HTTP layer maps it to:

```json
{
  "status": "error",
  "message": "Device already registered"
}
```

If `X-API-Key` is missing or invalid, the request returns `401 Unauthorized` through `UnauthorizedException` and the global exception handler.

### 2. Background runner to outbound MQTT

```text
DeviceRuntimeRunner
  -> every 5 seconds creates SendDeviceOnlineUseCase
  -> publishes DeviceOnlineEvent
  -> InMemoryEventBus dispatches to MQTTSendDeviceOnlineHandler
  -> publishes MQTT payload to topic device/online
```

Outbound payload shape:

```json
{
  "device_id": "your-device-id",
  "timestamp": "2026-05-15T12:34:56.789012+00:00"
}
```

### 3. Inbound MQTT routing

The application subscribes to:


| Topic             | QoS | Current state                         |
| ----------------- | --- | ------------------------------------- |
| `device/config`   | 0   | subscribed, no handler registered yet |
| `device/register` | 1   | handler registered                    |
| `device/publish`  | 1   | subscribed, no handler registered yet |


`MessageRouter` currently wires only `device/register` to `RegisterDeviceMessageHandler`.

> Note: in the current code, `RegisterDeviceMessageHandler` parses the MQTT payload correctly, but it calls `RegisterDeviceUseCase.execute(device_id=...)` while the use case expects a `RegisterDeviceInput` DTO. The HTTP path is complete; the MQTT registration path still needs that small alignment before it works end-to-end.

## Core Building Blocks

### Unit of Work

`RegisterDeviceUseCase` owns the transaction boundary:

```python
with self._uow as uow:
    existing_device = self._device_repository.get_by_id(input_dto.device_id)
    if existing_device is not None:
        return Err(DeviceError.DEVICE_ALREADY_REGISTERED)

    self._device_repository.save(device)
    uow.commit()
```

`PostgresUnitOfWork` borrows a connection from `ThreadedConnectionPool`, commits on success, rolls back on failure, then returns the connection to the pool.

### Result type

Expected business failures use `Ok[T] | Err[E]` instead of exceptions:

```python
Result = Ok[T] | Err[E]
```

The controller checks the result and lets the HTTP response helper format a consistent envelope.

### Shared state

`StateManager` is a singleton created at startup and protects mutable in-memory state with locks:

- `DeviceRuntimeState(can_publish: bool)`
- `ScreenshotState(url: str | None, should_send: bool)`

At the moment, device registration sets `can_publish=True`, but `DeviceRuntimeRunner` does not read that flag yet.

### Factories

Scoped factories build fresh use cases per request or runner iteration:

- `build_register_device_usecase()`
- `build_send_device_online_usecase()`

A singleton-style factory also exists for `CreateOrderUseCase`, which uses the pure `PricingService`. `CreateOrderUseCase` is currently built during bootstrap but is not exposed by any route or message handler yet.

## Configuration

Configuration is loaded from `.env` via `python-dotenv`.


| Variable                             | Default     |
| ------------------------------------ | ----------- |
| `DB_HOST`                            | `localhost` |
| `DB_PORT`                            | `5432`      |
| `DB_USER`                            | `postgres`  |
| `DB_PASSWORD`                        | `postgres`  |
| `DB_NAME`                            | `mydb`      |
| `DB_MIN_CONN`                        | `2`         |
| `DB_MAX_CONN`                        | `10`        |
| `DEVICE_ID`                          | `hardcode`  |
| `MQTT_BROKER`                        | `localhost` |
| `MQTT_PORT`                          | `1883`      |
| `MQTT_USERNAME`                      | empty       |
| `MQTT_PASSWORD`                      | empty       |
| `MQTT_USE_TLS`                       | `false`     |
| `HTTP_SERVER_HOST`                   | `0.0.0.0`   |
| `HTTP_SERVER_PORT`                   | `8000`      |
| `HTTP_SERVER_GRACE_PERIOD`           | `10`        |
| `HTTP_SERVER_REQUEST_TIMEOUT_PERIOD` | `30`        |
| `HTTP_SERVER_API_KEY`                | empty       |
| `LOGGER_LEVEL`                       | `20`        |
| `JWT_ALLOWED_ALGS`                   | `HS256`     |
| `JWT_ISSUER`                         | empty       |
| `JWT_SECRET_KEY`                     | empty       |
| `JWT_TOKEN_DURATION`                 | `0`         |


`JWT` and `LOGGER_LEVEL` are loaded into config today, but they are not used by the current request flow yet.

## Running the Project

### 1. Install dependencies

This repo includes `uv.lock`, so with `uv`:

```bash
uv sync
```

### 2. Start PostgreSQL

```bash
docker compose up -d postgres
```

The app runs yoyo migrations automatically on startup and creates the `device` table if needed.

### 3. Configure environment

Create or update `.env` as needed. The minimum useful values are typically:

```env
DEVICE_ID=my-device
HTTP_SERVER_API_KEY=your-api-key
MQTT_BROKER=localhost
DB_HOST=localhost
```

You also need an MQTT broker reachable by the configured host and port. `docker-compose.yml` currently starts PostgreSQL only; it does not provision MQTT.

### 4. Start the application

```bash
uv run python main.py
```

## Project Structure

```text
.
├── main.py
├── bootstrap/
│   ├── application.py
│   ├── container.py
│   ├── database.py
│   ├── event_bus.py
│   ├── http.py
│   ├── http_router.py
│   ├── message_router.py
│   ├── mqtt.py
│   └── usecase_factories/
├── config/
├── domain/
│   ├── entities/device.py
│   ├── errors/device_error.py
│   ├── events/device_online_event.py
│   └── services/pricing_service.py
├── application/
│   ├── dto/
│   ├── interfaces/
│   ├── state/
│   ├── result.py
│   └── usecase/
├── infrastructure/
│   ├── event_handlers/
│   ├── messaging/
│   ├── persistence/
│   └── runner/
└── presentation/
    ├── http/
    └── messaging/
```

## Current Implementation Notes

- PostgreSQL is the only service provided by `docker-compose.yml`.
- `InMemoryEventBus` is the active event bus; `kafka_event_bus.py` and `rabbitmq_event_bus.py` are placeholders.
- `presentation/messaging/kafka/kafka_consumer.py` is also still a placeholder.
- The active HTTP middleware is `LoggingMiddleware`; API-key auth is wired as a FastAPI dependency on the route.
- `SendDeviceOnlineUseCase` receives a `UnitOfWork`, but it does not use it yet.

