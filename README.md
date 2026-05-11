<p align="center">
  <img src="./architecture.svg" alt="Clean Architecture Diagram" width="420"/>
</p>

# Python Clean Event-Driven Architecture

A template project for building scalable Python applications using **Clean Architecture** and **Event-Driven** principles.  
This template demonstrates how to structure HTTP APIs, MQTT communication, background workers, domain events, and dependency injection in a clean and maintainable way — all running in a single process via threads.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Runtime Overview](#runtime-overview)
- [Flow 1 — HTTP Inbound → Controller → Use Case](#flow-1--http-inbound--controller--use-case)
- [Flow 2 — MQTT Inbound → Router → Use Case](#flow-2--mqtt-inbound--router--use-case)
- [Flow 3 — Thread Runner → Event Bus → MQTT Outbound](#flow-3--thread-runner--event-bus--mqtt-outbound)
- [Unit of Work — How Transactions Work](#unit-of-work--how-transactions-work)
- [Result Type — How Errors Are Handled](#result-type--how-errors-are-handled)
- [Error Enums — Typed Error Codes](#error-enums--typed-error-codes)
- [DTO — Input and Output Contracts](#dto--input-and-output-contracts)
- [State Manager — Shared In-Memory State](#state-manager--shared-in-memory-state)
- [Scoped vs Singleton Factories](#scoped-vs-singleton-factories)
- [Bootstrap — Composition Root](#bootstrap--composition-root)
- [Dependency Rules](#dependency-rules)
- [Project Structure](#project-structure)

---

## Architecture Overview

The system is composed of four strict layers.  
**Dependencies always point inward — outer layers know about inner layers, never the reverse.**

```
┌────────────────────────────────────────────────────────────────┐
│  Presentation                                                  │
│  HTTP routes, controllers, requests, responses, presenters     │
│  MQTT handlers, message router, Kafka consumer                 │
├────────────────────────────────────────────────────────────────┤
│  Application                                                   │
│  Use cases, DTOs, Result type                                  │
│  Interfaces: UnitOfWork, EventBus, DeviceRepository            │
│  StateManager, use case factories                              │
├────────────────────────────────────────────────────────────────┤
│  Domain                                                        │
│  Entities, events, errors, domain services                     │
│  (no external dependencies — stdlib only)                      │
├────────────────────────────────────────────────────────────────┤
│  Infrastructure                                                │
│  Postgres, MQTT client, InMemoryEventBus, runners              │
└────────────────────────────────────────────────────────────────┘
```

> Repository and event bus **interfaces** live in the **Application** layer (`application/interfaces/`),  
> not in the Domain. Domain only defines entities, events, errors, and domain services.

---

## Flow 1 — HTTP Inbound → Controller → Use Case

```
Client
  │
  │  POST /api/v1/devices/register
  │  Body: {"device_id": "PC_GAMINGKU"}
  ▼
ApiKeyMiddleware                             ← validates X-API-Key header
  │
  ▼
FastAPI router (device_routes.py)            ← presentation/http/routes/
  │  parses body → RegisterDeviceRequest (Pydantic)
  ▼
RegisterDeviceController.handle(request)     ← presentation/http/controllers/
  │  builds RegisterDeviceInput DTO
  ▼
RegisterDeviceUseCase.execute(input_dto)     ← application/usecase/
  │  [scoped: fresh instance per request]
  │
  ├── device_repository.get_by_id(id)
  │     → if exists: return Err(DeviceError.DEVICE_ALREADY_REGISTERED)
  │
  ├── device = Device(device_id, is_registered=True)
  │
  ├── with self._uow as uow:               ← UnitOfWork context manager
  │       device_repository.save(device)   ← app interface, no SQL knowledge
  │       uow.commit()
  │
  ├── state_manager.update_device_publish_permission(True)
  │
  └── return Ok(RegisterDeviceOutput)
        │
        ▼
DevicePresenter.to_response(output)          ← presentation/http/presenters/
  │  maps output DTO → RegisterDeviceData (Pydantic)
  ▼
http_response(ParamHTTPResp)
  │  wraps in Response envelope → JSONResponse
  ▼
Client receives:
  201 Created
  {"status": "success", "data": {"device_id": "cam-01", "status": "active"}}

  400 Bad Request (if already registered)
  {"status": "error", "message": "Device already registered"}
```

### Key files

| File | Role |
|------|------|
| `presentation/http/routes/device_routes.py` | FastAPI `APIRouter`, maps path → controller |
| `presentation/http/controllers/register_device_controller.py` | Parses request, calls use case, formats response |
| `presentation/http/requests/register_device_request.py` | Pydantic input validation |
| `presentation/http/presenters/device_presenter.py` | Maps output DTO → response schema |
| `presentation/http/responses/register_device_response.py` | Response body schema |
| `presentation/http/responses/shared/response_helper.py` | `http_response()` envelope builder |
| `application/usecase/register_device_usecase.py` | Business logic + transaction ownership |

---

## Flow 2 — MQTT Inbound → Router → Use Case

```
MQTT Broker
  │
  │  topic: "device/register"
  │  payload: {"device_id": "cam-01"}
  ▼
MqttClient.on_message(topic, payload)        ← infrastructure/messaging/mqtt/
  │  wired to router.dispatch at startup
  ▼
MessageRouter.dispatch(topic, payload)       ← presentation/messaging/router.py
  │  looks up handler by topic key
  ▼
RegisterDeviceMessageHandler.__call__()      ← presentation/messaging/mqtt/handlers/
  │  parses JSON, extracts device_id
  │  calls scoped factory → fresh use case instance
  ▼
RegisterDeviceUseCase.execute(input_dto)     ← same use case as HTTP flow
  │
  └── same transaction + state logic as Flow 1
```

### Subscribed topics

| Topic | Handler |
|-------|---------|
| `device/register` | `RegisterDeviceMessageHandler` |
| `device/config` | *(extensible)* |
| `device/publish` | *(extensible)* |

---

## Flow 3 — Thread Runner → Event Bus → MQTT Outbound

```
Thread (daemon=True, started in main.py)
  │
  ▼
DeviceRuntimeRunner.run()                    ← infrastructure/runner/
  │
  │  while True:
  │    usecase = create_usecase()            ← scoped factory, fresh per iteration
  │    usecase.execute(device_id)
  │    sleep(interval_seconds)              ← default: 5s
  ▼
SendDeviceOnlineUseCase.execute(device_id)   ← application/usecase/
  │
  │  creates domain event
  ▼
DeviceOnlineEvent(device_id, timestamp)      ← domain/events/
  │
  ▼
EventBus.publish(event)                      ← application/interfaces/messaging/event_bus.py
  │  concrete impl: InMemoryEventBus
  ▼
InMemoryEventBus                             ← infrastructure/messaging/event_bus/
  │  iterates subscribed handlers for DeviceOnlineEvent
  ▼
MQTTSendDeviceOnlineHandler.__call__(event)  ← infrastructure/event_handlers/
  │  serializes → DeviceOnlineMessage
  ▼
MqttClient.publish(
    topic="device/online",
    payload=message.to_bytes()
)
  │
  ▼
MQTT Broker
```

> The use case only knows `EventBus` — it never knows MQTT exists.  
> Swapping MQTT for Kafka requires only changing the handler registration in `bootstrap/event_bus.py`.

---

## Unit of Work — How Transactions Work

The `UnitOfWork` pattern ensures the use case owns the transaction boundary; the repository just executes SQL.

```
application/interfaces/persistence/unit_of_work.py   ← abstract contract (Application layer)
        ↑ implemented by
infrastructure/persistence/database/postgres_unit_of_work.py
```

### Inside the use case

```python
# application/usecase/register_device_usecase.py

with self._uow as uow:               # __enter__: borrow connection from pool
    self._device_repository.save(device)
    uow.commit()                     # explicit commit
                                     # __exit__: rollback on exception, return to pool
```

### Inside `PostgresUnitOfWork`

```
__enter__   → conn = pool.getconn()   (borrow from pool)
commit()    → conn.commit()
rollback()  → conn.rollback()
__exit__    → if exception: rollback()
             pool.putconn(conn)        (return to pool)
```

### Inside repositories

```
BaseRepository.cursor
  └── self._uow.connection.cursor()

PostgresDeviceRepository(BaseRepository, DeviceRepository)
  └── self.cursor.execute(SQL)        ← cursor from active UoW connection
```

### Why the application repository interface has no `Tx` parameter

```python
# application/interfaces/persistence/repositories/device_repository.py
class DeviceRepository(ABC):
    def save(self, device: Device) -> None: ...
    def get_by_id(self, device_id: str) -> Device | None: ...
    def exists(self, device_id: str) -> bool: ...
    def delete(self, device_id: str) -> None: ...
```

The repository speaks the **business language** (save a Device), not SQL.  
The `UnitOfWork` lives in the Application layer — the domain never knows it exists.

---

## Result Type — How Errors Are Handled

Instead of raising exceptions for expected errors, use cases return a `Result` type.

```python
# application/result.py
Result = Ok[T] | Err[E]
```

```
RegisterDeviceUseCase.execute()
  │
  ├── device exists?   → return Err(DeviceError.DEVICE_ALREADY_REGISTERED)
  │
  └── success?         → return Ok(RegisterDeviceOutput(...))
```

Controller checks the result:

```python
result = usecase.execute(input_dto)

if result.is_err():
    return http_response(ParamHTTPResp(code=400, err=result.error))

return http_response(ParamHTTPResp(code=201, data=presenter.to_response(result.value)))
```

---

## Error Enums — Typed Error Codes

Errors are typed `str` enums. The `ERROR_MAP` in `presentation/http/responses/shared/error_messages.py` maps each error code to a human-readable message sent to the client.

| Enum | Location | Values |
|------|----------|--------|
| `DeviceError` | `domain/errors/device_error.py` | `device_already_registered`, `device_not_found` |
| `SystemError` | `presentation/http/errors/system_error.py` | `internal_server_error` |
| `AuthError` | `presentation/http/errors/auth_error.py` | `unauthorized`, `invalid_credentials` |

`global_exception_handler` in `presentation/http/exception_handlers/` catches any unhandled exception and returns a `500` with `SystemError.INTERNAL_SERVER_ERROR`.

---

## DTO — Input and Output Contracts

Use cases do not receive raw request objects or return domain entities directly.  
They communicate through **DTOs** defined in the Application layer.

```
Presentation                    Application                     Domain
RegisterDeviceRequest  →  RegisterDeviceInput  →  (use case)  →  Device entity
(Pydantic)                (dataclass)                              (dataclass)

                          RegisterDeviceOutput  ←  (use case)
                          (dataclass)
                                │
DevicePresenter         ←       │
RegisterDeviceData      (maps output → response schema)
(Pydantic)
```

| File | Type | Direction |
|------|------|-----------|
| `application/dto/input/register_device_input.py` | `RegisterDeviceInput` | Presentation → Application |
| `application/dto/output/register_device_output.py` | `RegisterDeviceOutput` | Application → Presentation |
| `presentation/http/requests/register_device_request.py` | `RegisterDeviceRequest` | HTTP body → Controller |
| `presentation/http/responses/register_device_response.py` | `RegisterDeviceData` | Presenter → HTTP body |

---

## State Manager — Shared In-Memory State

`StateManager` holds application-level state shared across threads. All mutations are protected by `threading.Lock`.

```
StateManager
  ├── _device_lock      → guards DeviceRuntimeState
  │     └── DeviceRuntimeState(can_publish: bool)
  │
  └── _screenshot_lock  → guards ScreenshotState
        └── ScreenshotState(url: str | None, should_send: bool)
```

| Method | Description |
|--------|-------------|
| `update_device_publish_permission(bool)` | Set whether the device is allowed to publish |
| `can_device_publish()` | Check publish permission (thread-safe read) |
| `get_device_runtime_state()` | Return a snapshot of `DeviceRuntimeState` |
| `update_screenshot_state(url, should_send)` | Update screenshot state |
| `get_screenshot_state()` | Return a snapshot of `ScreenshotState` |
| `reset_screenshot_state()` | Reset screenshot state to defaults |

`StateManager` is created once in `build_application()` and injected as a singleton into all use cases that need it.

---

## Scoped vs Singleton Factories

### Scoped factories — fresh instance per call

Use cases that own a `UnitOfWork` are **scoped**: a new instance is created per HTTP request, MQTT message, or runner iteration. This ensures each call gets its own database connection from the pool.

```python
# bootstrap/usecase_factories/scoped_factories.py

def build_register_device_usecase(container) -> RegisterDeviceUseCase:
    uow = PostgresUnitOfWork(pool=container.pool)          # fresh UoW per call
    device_repository = PostgresDeviceRepository(uow=uow)  # fresh repo per call
    return RegisterDeviceUseCase(uow, state_manager, device_repository)

def build_send_device_online_usecase(container) -> SendDeviceOnlineUseCase:
    uow = PostgresUnitOfWork(pool=container.pool)
    return SendDeviceOnlineUseCase(uow=uow, event_bus=container.event_bus)
```

The controller receives a `Callable[[], UseCase]` factory, not the use case directly:

```python
class RegisterDeviceController:
    def __init__(self, usecase_factory: Callable[[], RegisterDeviceUseCase]):
        self._factory = usecase_factory

    async def handle(self, request):
        usecase = self._factory()   # new instance per request
        ...
```

### Singleton factories — shared instance

Stateless use cases that hold no connection or mutable state are built **once** and reused.

```python
# bootstrap/usecase_factories/singleton_factories.py

def build_create_order_usecase(pricing_service) -> CreateOrderUseCase:
    return CreateOrderUseCase(pricing_service=pricing_service)
```

`CreateOrderUseCase` uses `PricingService` (a pure domain service) — no DB, no UoW, so one instance is shared for the lifetime of the application.

---

## Bootstrap — Composition Root

`bootstrap/application.py` is the **only place** where all layers are wired together.

```
build_application()
  │
  ├── load_config()                              → Config (Device, DB, HTTP, MQTT, JWT, Logger)
  ├── init_database(config.database)             → ThreadedConnectionPool
  ├── StateManager()                             → in-memory state
  ├── InMemoryEventBus()                         → event bus
  ├── build_mqtt_client(config)                  → MqttClient
  │
  ├── ApplicationContainer(pool, state, bus, mqtt)
  │
  ├── register_events(container)
  │     └── event_bus.subscribe(DeviceOnlineEvent, MQTTSendDeviceOnlineHandler)
  │
  ├── build_pricing_service()                    → PricingService (singleton)
  ├── build_create_order_usecase(pricing_service) → CreateOrderUseCase (singleton)
  │
  ├── register_message_handlers(router, factory)
  │     └── router.register("device/register", RegisterDeviceMessageHandler)
  │
  ├── mqtt_client.on_message = router.dispatch
  │   mqtt_client.connect()
  │   mqtt_client.subscribe([("device/config",0), ("device/register",1), ("device/publish",1)])
  │
  ├── DeviceRuntimeRunner(create_usecase=lambda: build_send_device_online_usecase(...))
  │
  ├── build_fastapi_app(container, config.http)
  │     └── global_exception_handler
  │     └── ApiKeyMiddleware
  │     └── register_http_routes → make_device_router(lambda: build_register_device_usecase(...))
  │
  └── return Application(device_runtime_runner, uvicorn_config)
```

---

## Dependency Rules

```
Presentation   →  Application  →  Domain
Infrastructure →  Application  →  Domain
                                  Domain → (nothing — stdlib only)
Bootstrap      →  ALL layers   (composition root only)
```

| Layer | Can import | Cannot import |
|-------|-----------|---------------|
| Domain | stdlib only | Everything else |
| Application | Domain | Infrastructure, Presentation |
| Infrastructure | Domain, Application | Presentation |
| Presentation | Domain, Application | Infrastructure |
| Bootstrap | Everything | — |

---

## Project Structure

```
py-clean-event-driven-architecture/
│
├── main.py                                    # entry point: Thread(runner) + uvicorn
│
├── bootstrap/                                 # composition root — wires all layers
│   ├── application.py                         # build_application() ← start here
│   ├── container.py                           # ApplicationContainer dataclass
│   ├── database.py                            # init_database() → ThreadedConnectionPool
│   ├── event_bus.py                           # register_events(container)
│   ├── http.py                                # build_fastapi_app(), build_uvicorn_config()
│   ├── http_router.py                         # register_http_routes(app, container)
│   ├── message_router.py                      # register_message_handlers(router, factory)
│   ├── mqtt.py                                # build_mqtt_client(config)
│   ├── services.py                            # build_pricing_service() → PricingService
│   └── usecase_factories/
│       ├── scoped_factories.py                # fresh UseCase per call (HTTP/MQTT/runner)
│       └── singleton_factories.py             # shared UseCase (stateless)
│
├── config/                                    # typed config loading from env
│   ├── config.py                              # Config(device, database, http, mqtt, jwt, logger)
│   ├── database.py                            # DatabaseConfig
│   ├── device.py                              # DeviceConfig
│   ├── http.py                                # HttpServerConfig
│   ├── jwt.py                                 # JwtConfig
│   ├── logger.py                              # LoggerConfig
│   └── mqtt.py                                # MQTTConfig
│
├── domain/                                    # innermost — no external dependencies
│   ├── entities/
│   │   └── device.py                          # Device(device_id, is_registered)
│   ├── errors/
│   │   └── device_error.py                    # DeviceError enum (str + Enum)
│   ├── events/
│   │   └── device_online_event.py             # DeviceOnlineEvent(device_id, timestamp)
│   ├── exceptions/                            # (extensible) domain exception types
│   ├── policies/                              # (extensible) domain policy objects
│   ├── services/
│   │   └── pricing_service.py                 # PricingService — pure calculation
│   └── value_objects/                         # (extensible) value object types
│
├── application/                               # use cases + application-level contracts
│   ├── dto/
│   │   ├── input/
│   │   │   └── register_device_input.py       # RegisterDeviceInput
│   │   └── output/
│   │       └── register_device_output.py      # RegisterDeviceOutput
│   ├── interfaces/
│   │   ├── messaging/
│   │   │   └── event_bus.py                   # EventBus ABC (publish, subscribe)
│   │   └── persistence/
│   │       ├── repositories/
│   │       │   └── device_repository.py       # DeviceRepository ABC — no Tx, no SQL
│   │       └── unit_of_work.py                # UnitOfWork ABC (__enter__, commit, rollback)
│   ├── result.py                              # Ok[T] | Err[E] Result type
│   ├── state/
│   │   ├── device_runtime_state.py            # DeviceRuntimeState(can_publish)
│   │   ├── screenshot_state.py                # ScreenshotState(url, should_send)
│   │   └── state_manager.py                   # thread-safe in-memory state facade
│   └── usecase/
│       ├── create_order_usecase.py            # singleton — uses PricingService only
│       ├── register_device_usecase.py         # scoped — owns transaction + state update
│       └── send_device_online_usecase.py      # scoped — publishes DeviceOnlineEvent
│
├── infrastructure/                            # all external concerns
│   ├── event_handlers/
│   │   └── mqtt_send_device_online_handler.py # DeviceOnlineEvent → MQTT publish
│   ├── external_services/                     # (extensible) third-party API clients
│   ├── inference/                             # (extensible) ML inference adapters
│   ├── messaging/
│   │   ├── event_bus/
│   │   │   ├── in_memory_event_bus.py         # InMemoryEventBus (default)
│   │   │   ├── kafka_event_bus.py             # KafkaEventBus (swappable)
│   │   │   └── rabbitmq_event_bus.py          # RabbitMQEventBus (swappable)
│   │   └── mqtt/
│   │       ├── mqtt_client.py                 # paho-mqtt wrapper
│   │       └── messages/
│   │           └── device_online_message.py   # MQTT payload DTO
│   ├── persistence/
│   │   ├── database/
│   │   │   ├── database.py                    # Database (pool init, migrate)
│   │   │   ├── postgres_unit_of_work.py       # PostgresUnitOfWork (context manager)
│   │   │   └── migrations/
│   │   │       └── init_schema.py             # initial schema migration
│   │   └── repositories/
│   │       ├── base_repository.py             # BaseRepository (exposes cursor via UoW)
│   │       └── device/
│   │           └── postgres_device_repository.py
│   ├── runner/
│   │   └── device_runtime_runner.py           # while True → SendDeviceOnlineUseCase
│   └── shared/                                # (extensible) shared infra utilities
│
└── presentation/                              # entry points from the external world
    ├── http/
    │   ├── controllers/
    │   │   └── register_device_controller.py  # orchestrates request → use case → response
    │   ├── errors/
    │   │   ├── auth_error.py                  # AuthError enum (unauthorized, invalid_credentials)
    │   │   └── system_error.py                # SystemError enum (internal_server_error)
    │   ├── exception_handlers/
    │   │   └── global_exception_handler.py    # catches all unhandled exceptions → 500
    │   ├── middleware/
    │   │   └── api_key_middleware.py           # X-API-Key validation
    │   ├── presenters/
    │   │   └── device_presenter.py            # output DTO → response schema
    │   ├── requests/
    │   │   └── register_device_request.py     # Pydantic input validation
    │   ├── responses/
    │   │   ├── register_device_response.py    # RegisterDeviceData schema
    │   │   └── shared/
    │   │       ├── base_response.py           # Response[T] envelope
    │   │       ├── error_messages.py          # ERROR_MAP: error code → human message
    │   │       ├── response_constants.py      # SUCCESS / ERROR / status constants
    │   │       └── response_helper.py         # http_response() builder
    │   └── routes/
    │       └── device_routes.py               # FastAPI APIRouter
    └── messaging/
        ├── router.py                          # MessageRouter (topic → handler)
        ├── kafka/
        │   └── kafka_consumer.py              # (extensible) Kafka consumer entry point
        └── mqtt/
            ├── mqtt_consumer.py               # MQTT consumer entry point
            ├── handlers/
            │   └── register_device_message_handler.py
            └── requests/
                └── register_device_request.py # MQTT payload schema
```
