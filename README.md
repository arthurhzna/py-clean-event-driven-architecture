<p align="center">
  <img src="./architecture.svg" alt="Clean Architecture Diagram" width="420"/>
</p>

# Python Clean Event-Driven Architecture

A real-time device monitoring system built with **Clean Architecture** and **Event-Driven** principles.  
The system exposes an HTTP API, connects to an MQTT broker, processes inbound device messages, and continuously publishes device heartbeat events — all running in a single process via threads.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Runtime Overview](#runtime-overview)
- [Flow 1 — HTTP Inbound → Controller → Use Case](#flow-1--http-inbound--controller--use-case)
- [Flow 2 — MQTT Inbound → Router → Use Case](#flow-2--mqtt-inbound--router--use-case)
- [Flow 3 — Thread Runner → Event Bus → MQTT Outbound](#flow-3--thread-runner--event-bus--mqtt-outbound)
- [Unit of Work — How Transactions Work](#unit-of-work--how-transactions-work)
- [Result Type — How Errors Are Handled](#result-type--how-errors-are-handled)
- [DTO — Input and Output Contracts](#dto--input-and-output-contracts)
- [Scoped Factories — Use Case Lifecycle](#scoped-factories--use-case-lifecycle)
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
│  MQTT handlers, message router                                 │
├────────────────────────────────────────────────────────────────┤
│  Application                                                   │
│  Use cases, DTOs, Result type, UnitOfWork interface            │
│  StateManager, use case factories                              │
├────────────────────────────────────────────────────────────────┤
│  Domain                                                        │
│  Entities, events, errors, ports (repository + event bus)      │
├────────────────────────────────────────────────────────────────┤
│  Infrastructure                                                │
│  Postgres, MQTT client, InMemoryEventBus, runners              │
└────────────────────────────────────────────────────────────────┘
```

---

## Runtime Overview

`main.py` starts two concurrent workers in a single process:

```
main.py
  │
  ├── Thread(daemon=True)
  │     └── DeviceRuntimeRunner.run()   ← while True loop, publishes heartbeat
  │
  └── uvicorn.run(app)                  ← FastAPI HTTP server + MQTT listener
```

---

## Flow 1 — HTTP Inbound → Controller → Use Case

```
Client
  │
  │  POST /api/v1/devices/register
  │  Body: {"device_id": "cam-01"}
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
  │       device_repository.save(device)   ← domain port, no SQL knowledge
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
  {"status": "error", "message": "device_already_registered"}
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
  │    sleep(5)
  ▼
SendDeviceOnlineUseCase.execute(device_id)   ← application/usecase/
  │
  │  creates domain event
  ▼
DeviceOnlineEvent(device_id, timestamp)      ← domain/events/
  │
  ▼
BaseEventBus.publish(event)                  ← domain/ports/messaging/event_bus.py
  │  concrete impl: InMemoryEventBus
  ▼
InMemoryEventBus                             ← infrastructure/event_bus/
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

> The use case only knows `BaseEventBus` — it never knows MQTT exists.  
> Swapping MQTT for Kafka requires only changing the handler registration in `bootstrap/event_bus.py`.

---

## Unit of Work — How Transactions Work

The `UnitOfWork` pattern replaces the old `Tx`-in-domain approach.  
The use case owns the transaction boundary; the repository just executes SQL.

```
application/interface/persistence/unit_of_work.py   ← abstract contract (Application layer)
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

### Why domain repository has no `Tx` parameter

```python
# domain/ports/repositories/device_repository.py  ← clean, no SQL concepts
class DeviceRepository(ABC):
    def save(self, device: Device) -> None: ...
    def get_by_id(self, device_id: str) -> Device | None: ...
```

The domain repository speaks the **business language** (save a Device), not SQL.  
The `UnitOfWork` lives in the Application layer — domain never knows it exists.

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

Domain errors live in `domain/errors/device_error.py` as `Enum` values, mapped to human-readable messages in `presentation/http/responses/shared/error_messages.py`.

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

## Scoped Factories — Use Case Lifecycle

Use cases are **not singletons**. A fresh instance is created per HTTP request or MQTT message.  
This ensures each request gets its own `UnitOfWork` and clean connection from the pool.

```python
# bootstrap/http_router.py
app.include_router(
    make_device_router(
        lambda: build_register_device_usecase(container=container)
    )
)
```

```python
# bootstrap/usecase_factories/scoped_factories.py
def build_register_device_usecase(container) -> RegisterDeviceUseCase:
    uow = PostgresUnitOfWork(pool=container.pool)          # fresh UoW per call
    device_repository = PostgresDeviceRepository(uow=uow)  # fresh repo per call
    return RegisterDeviceUseCase(uow, state_manager, device_repository)
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

---

## Bootstrap — Composition Root

`bootstrap/application.py` is the **only place** where all layers are wired together.

```
build_application()
  │
  ├── load_config()                              → Config (DB, MQTT, HTTP, Device)
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
  ├── register_message_handlers(router, factory)
  │     └── router.register("device/register", RegisterDeviceMessageHandler)
  │
  ├── mqtt_client.on_message = router.dispatch
  │   mqtt_client.connect()
  │   mqtt_client.subscribe([("device/config",0), ("device/register",1), ...])
  │
  ├── DeviceRuntimeRunner(create_usecase=lambda: build_send_device_online_usecase(...))
  │
  ├── build_fastapi_app(container, config.http)
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
                                  Domain → (nothing)
Bootstrap      →  ALL layers   (composition root only)
```

| Layer | Can import | Cannot import |
|-------|-----------|---------------|
| Domain | stdlib only | Everything |
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
├── bootstrap/                                 # composition root
│   ├── application.py                         # build_application() ← start here
│   ├── container.py                           # ApplicationContainer dataclass
│   ├── database.py                            # init_database() → pool
│   ├── event_bus.py                           # register_events(container)
│   ├── http.py                                # build_fastapi_app(), build_uvicorn_config()
│   ├── http_router.py                         # register_http_routes(app, container)
│   ├── message_router.py                      # register_message_handlers(router, factory)
│   ├── mqtt.py                                # build_mqtt_client(config)
│   ├── services.py                            # PricingService (singleton)
│   └── usecase_factories/
│       ├── scoped_factories.py                # fresh UseCase per call (HTTP/MQTT)
│       └── singleton_factories.py             # shared UseCase (stateless)
│
├── config/                                    # typed config loading
│
├── domain/                                    # innermost — no dependencies
│   ├── entities/
│   │   └── device.py                          # Device(device_id, is_registered)
│   ├── errors/
│   │   └── device_error.py                    # DeviceError enum
│   ├── events/
│   │   └── device_online_event.py             # DeviceOnlineEvent(device_id, timestamp)
│   └── ports/
│       ├── messaging/
│       │   └── event_bus.py                   # BaseEventBus (publish, subscribe)
│       └── repositories/
│           └── device_repository.py           # DeviceRepository ABC — no Tx, no SQL
│
├── application/                               # use cases + application-level contracts
│   ├── dto/
│   │   ├── input/
│   │   │   └── register_device_input.py       # RegisterDeviceInput
│   │   └── output/
│   │       └── register_device_output.py      # RegisterDeviceOutput
│   ├── interface/
│   │   └── persistence/
│   │       └── unit_of_work.py                # UnitOfWork ABC (__enter__, commit, rollback)
│   ├── result.py                              # Ok[T] | Err[E] Result type
│   ├── state/
│   │   └── state_manager.py                   # thread-safe in-memory state
│   └── usecase/
│       ├── register_device_usecase.py         # HTTP + MQTT registration, owns transaction
│       └── send_device_online_usecase.py      # publishes DeviceOnlineEvent
│
├── infrastructure/                            # all external concerns
│   ├── event_bus/
│   │   ├── in_memory_event_bus.py             # InMemoryEventBus
│   │   ├── kafka_event_bus.py                 # KafkaEventBus (swappable)
│   │   └── rabbitmq_event_bus.py              # RabbitMQEventBus (swappable)
│   ├── event_handlers/
│   │   └── mqtt_send_device_online_handler.py # DeviceOnlineEvent → MQTT publish
│   ├── messaging/
│   │   └── mqtt/
│   │       ├── mqtt_client.py                 # paho-mqtt wrapper
│   │       └── messages/
│   │           └── device_online_message.py   # MQTT payload DTO
│   ├── persistence/
│   │   ├── database/
│   │   │   ├── database.py                    # Database (pool, migrate)
│   │   │   ├── postgres_unit_of_work.py       # PostgresUnitOfWork (context manager)
│   │   │   └── migrations/
│   │   └── repositories/
│   │       ├── base_repository.py             # BaseRepository (exposes cursor via UoW)
│   │       └── device/
│   │           └── postgres_device_repository.py
│   └── runner/
│       └── device_runtime_runner.py           # while True → SendDeviceOnlineUseCase
│
└── presentation/                              # entry points from external world
    ├── http/
    │   ├── controllers/
    │   │   └── register_device_controller.py  # orchestrates request → use case → response
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
    │   │       ├── error_messages.py          # error code → human message map
    │   │       └── response_helper.py         # http_response() builder
    │   └── routes/
    │       └── device_routes.py               # FastAPI APIRouter
    └── messaging/
        ├── router.py                          # MessageRouter (topic → handler)
        └── mqtt/
            └── handlers/
                └── register_device_message_handler.py
```
