<p align="center">
  <img src="./architecture.svg" alt="Clean Architecture Diagram" width="420"/>
</p>

# Python Clean Event-Driven Architecture
---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Flow 1 — MQTT Inbound → Router → Use Case](#flow-1--mqtt-inbound--router--use-case)
- [Flow 2 — while True Runner → Event Bus → MQTT Outbound](#flow-2--while-true-runner--event-bus--mqtt-outbound)
- [Flow 3 — Use Case → Interface → Infrastructure (Repository + Tx)](#flow-3--use-case--interface--infrastructure-repository--tx)
- [Dependency Rules](#dependency-rules)
- [Bootstrap — Composition Root](#bootstrap--composition-root)
- [Project Structure](#project-structure)

---

## Architecture Overview

The system is composed of four strict layers.  
**Dependencies always point inward — outer layers know about inner layers, never the reverse.**

```
┌─────────────────────────────────────────────┐
│              Presentation                   │  MQTT handlers, message router
├─────────────────────────────────────────────┤
│              Application                    │  Use cases, state manager, interfaces
├─────────────────────────────────────────────┤
│               Domain                        │  Entities, events, repository contracts, Tx protocol
├─────────────────────────────────────────────┤
│            Infrastructure                   │  Postgres, MQTT client, event bus, runners
└─────────────────────────────────────────────┘
```

There are two main runtime loops running in parallel:

| Loop | Purpose |
|------|---------|
| **MQTT listener** | Receives inbound messages from the broker, routes to use cases |
| **`while True` runner** | Periodically publishes device heartbeat via event bus |

---

## Flow 1 — MQTT Inbound → Router → Use Case

When a device sends a registration message to the broker:

```
MQTT Broker  (external)
     │
     │  topic: "camera/register"
     │  payload: {"device_id": 42}
     ▼
MqttClient.on_message(topic, payload)        ← infrastructure/messaging/mqtt/mqtt_client.py
     │
     │  callback wired in bootstrap
     ▼
MessageRouter.dispatch(topic, payload)       ← presentation/messaging/router.py
     │
     │  looks up handler by topic
     ▼
RegisterDeviceMessageHandler.__call__()      ← presentation/messaging/mqtt/handlers/
     │  parses JSON payload
     │  extracts device_id: int
     ▼
RegisterDeviceUseCase.execute(device_id)     ← application/usecase/
     │
     │  wraps in atomic transaction
     ▼
DataStore.atomic(operation)                  ← application interface → infra impl
     │
     ├─► StateManager.update_device_registration(True)
     │
     └─► DeviceRepository.save(tx, device)   ← domain interface
               │
               ▼
         PostgresDeviceRepository.save()     ← infrastructure/persistence/repositories/
               │
               ▼
         tx.execute(INSERT INTO device ...)  ← infrastructure/persistence/database/tx.py
               │
               ▼
         PostgreSQL Database
```

### Key files

| File | Role |
|------|------|
| `infrastructure/messaging/mqtt/mqtt_client.py` | Connects to broker, receives raw bytes |
| `presentation/messaging/router.py` | Maps topic string → handler callable |
| `presentation/messaging/mqtt/handlers/register_device_message_handler.py` | Parses payload, calls use case |
| `application/usecase/register_device_usecase.py` | Business logic, owns the transaction |
| `infrastructure/persistence/database/datastore.py` | Manages connection pool + commit/rollback |
| `infrastructure/persistence/repositories/device/postgres_device_repository.py` | SQL implementation |

### How MessageRouter works

```
router = MessageRouter()

router.register("camera/register", RegisterDeviceMessageHandler(...))

# when MQTT message arrives:
router.dispatch("camera/register", b'{"device_id": 42}')
# → finds handler by topic key → calls handler(topic, payload)
```

---

## Flow 2 — while True Runner → Event Bus → MQTT Outbound

Every 5 seconds, the device broadcasts that it is online:

```
DeviceRuntimeRunner.run()                    ← infrastructure/runner/device_runtime_runner.py
     │
     │  while True: sleep(5)
     ▼
SendDeviceOnlineUseCase.execute(device_id)   ← application/usecase/
     │
     │  creates domain event
     ▼
DeviceOnlineEvent(device_id, timestamp)      ← domain/events/device_online_event.py
     │
     ▼
BaseEventBus.publish(event)                  ← domain/interface/messaging/event_bus.py
     │
     │  concrete impl: InMemoryEventBus
     ▼
InMemoryEventBus                             ← infrastructure/event_bus/in_memory_event_bus.py
     │
     │  looks up subscribed handlers for DeviceOnlineEvent
     ▼
MQTTSendDeviceOnlineHandler.__call__(event)  ← infrastructure/event_handlers/
     │
     │  serializes event → DeviceOnlineMessage
     ▼
MqttClient.publish(                          ← infrastructure/messaging/mqtt/mqtt_client.py
    topic="device/online",
    payload=message.to_bytes()
)
     │
     ▼
MQTT Broker  (external)
```

### Key files

| File | Role |
|------|------|
| `infrastructure/runner/device_runtime_runner.py` | `while True` loop, calls use case on interval |
| `application/usecase/send_device_online_usecase.py` | Creates event, publishes to event bus |
| `domain/events/device_online_event.py` | Pure domain event, no dependencies |
| `domain/interface/messaging/event_bus.py` | Abstract `BaseEventBus` — `publish` + `subscribe` |
| `infrastructure/event_bus/in_memory_event_bus.py` | Concrete in-process event bus |
| `infrastructure/event_handlers/mqtt_send_device_online_handler.py` | Subscribes to event, sends via MQTT |
| `infrastructure/messaging/mqtt/messages/device_online_message.py` | MQTT payload DTO |

### How EventBus works

```
# Subscribe (done once at startup in bootstrap/event_bus.py)
event_bus.subscribe(DeviceOnlineEvent, MQTTSendDeviceOnlineHandler(mqtt_client))

# Publish (done by use case at runtime)
event_bus.publish(DeviceOnlineEvent(device_id="cam-01", timestamp=...))

# InMemoryEventBus internally:
# handlers = self._handlers[DeviceOnlineEvent]
# for handler in handlers: handler(event)
```

The **use case only knows `BaseEventBus`** — it never knows MQTT exists.  
Swapping MQTT for Kafka only requires changing the handler in bootstrap.

---

## Flow 3 — Use Case → Interface → Infrastructure (Repository + Tx)

This shows how the use case interacts with the database without ever depending on Postgres directly.

### Layer contracts

```
domain/interface/persistence/tx.py           ← Tx Protocol (execute, fetchone)
domain/interface/repositories/               ← DeviceRepository ABC (save, get_by_id, ...)
application/interface/persistence/           ← DataStore ABC (atomic, query)
        ↑ implemented by
infrastructure/persistence/database/tx.py    ← Tx wraps psycopg2 cursor
infrastructure/persistence/database/         ← DataStore manages connection pool
infrastructure/persistence/repositories/     ← PostgresDeviceRepository
```

### Transaction flow inside `RegisterDeviceUseCase`

```python
# application/usecase/register_device_usecase.py

def execute(self, device_id: int) -> None:

    def operation(tx: Tx) -> None:            # tx = domain interface, not psycopg2
        device = Device(device_id=device_id, is_registered=True)
        self._device_repository.save(tx, device)
        self._state_manager.update_device_registration(True)

    self._datastore.atomic(operation)         # commits on success, rolls back on error
```

### What `DataStore.atomic()` does

```
DataStore.atomic(operation)
  │
  ├─ conn = pool.getconn()          # borrow from connection pool
  ├─ tx = Tx(conn)                  # wrap in Tx (infrastructure impl)
  ├─ operation(tx)                  # run use case callback
  ├─ conn.commit()      ✅ success
  │  conn.rollback()    ❌ exception
  └─ pool.putconn(conn)             # return to pool
```

### Why `Tx` lives in domain, not infrastructure

```
domain/interface/persistence/tx.py

class Tx(Protocol):
    def execute(self, query: str, params: tuple) -> None: ...
    def fetchone(self) -> tuple | None: ...
```

- Domain defines **what a transaction looks like** (Protocol = structural typing)
- Infrastructure `Tx` satisfies it without importing domain
- Repository receives `tx: Tx` (domain type) — never psycopg2 directly
- In tests, pass a `FakeTx` that satisfies the same Protocol

---

## Dependency Rules

```
Presentation   →  Application  →  Domain
Infrastructure →  Application  →  Domain
                                  Domain  → (nothing)
```

| Layer | Can import from | Cannot import from |
|-------|----------------|--------------------|
| Domain | — | Application, Infrastructure, Presentation |
| Application | Domain | Infrastructure, Presentation |
| Infrastructure | Domain, Application | Presentation |
| Presentation | Application, Domain | Infrastructure |

---

## Bootstrap — Composition Root

`infrastructure/bootstrap/application.py` is the **only place** where all layers are wired together.

```
build_application()
  │
  ├── 1. init_database()              → DataStore  (infra)
  ├── 2. StateManager()               → in-memory state  (application)
  ├── 3. InMemoryEventBus()           → event bus  (infra)
  ├── 4. MqttClient(broker_url)       → MQTT connection  (infra)
  │
  ├── 5. ApplicationContainer(...)    → holds all shared dependencies
  │
  ├── 6. register_events(container)
  │       └── event_bus.subscribe(DeviceOnlineEvent, MQTTSendDeviceOnlineHandler)
  │
  ├── 7. build_device_repository()    → PostgresDeviceRepository
  │
  ├── 8. build_register_device_usecase(container, device_repository)
  │       └── RegisterDeviceUseCase(datastore, state_manager, device_repository)
  │
  ├── 9. build_send_device_online_usecase(container)
  │       └── SendDeviceOnlineUseCase(event_bus)
  │
  ├── 10. MessageRouter()
  │        └── configure_message_router(router, register_device_usecase)
  │            └── router.register("camera/register", RegisterDeviceMessageHandler)
  │
  ├── 11. mqtt_client.on_message = router.dispatch   ← wire MQTT → router
  │        mqtt_client.connect()
  │        mqtt_client.subscribe("camera/register")
  │
  └── 12. DeviceRuntimeRunner(send_device_online_usecase)
           └── returns Application(container, mqtt_client, device_runtime_runner)
```

---

## Project Structure

```
py-clean-event-driven-architecture/
│
├── domain/                                    # innermost — no dependencies
│   ├── entities/
│   │   └── device.py                          # Device(device_id, is_registered)
│   ├── events/
│   │   └── device_online_event.py             # DeviceOnlineEvent(device_id, timestamp)
│   └── interface/
│       ├── messaging/
│       │   └── event_bus.py                   # BaseEventBus (publish, subscribe)
│       ├── persistence/
│       │   └── tx.py                          # Tx Protocol (execute, fetchone)
│       └── repositories/
│           └── device_repository.py           # DeviceRepository ABC
│
├── application/                               # use cases + application interfaces
│   ├── interface/
│   │   └── persistence/
│   │       └── datastore.py                   # DataStore ABC (atomic, query)
│   ├── state/
│   │   └── state_manager.py                   # thread-safe in-memory state
│   └── usecase/
│       ├── register_device_usecase.py         # handles device registration + DB write
│       └── send_device_online_usecase.py      # publishes DeviceOnlineEvent
│
├── infrastructure/                            # all external concerns
│   ├── bootstrap/
│   │   ├── application.py                     # composition root ← start here
│   │   ├── container.py                       # ApplicationContainer dataclass
│   │   ├── database.py                        # init_database() → DataStore
│   │   ├── event_bus.py                       # register_events(container)
│   │   ├── message_router.py                  # configure_message_router(...)
│   │   ├── repository.py                      # build_device_repository()
│   │   └── usecases.py                        # build_*_usecase() factories
│   ├── event_bus/
│   │   └── in_memory_event_bus.py             # InMemoryEventBus (pub/sub in-process)
│   ├── event_handlers/
│   │   └── mqtt_send_device_online_handler.py # DeviceOnlineEvent → MQTT publish
│   ├── messaging/
│   │   └── mqtt/
│   │       ├── mqtt_client.py                 # paho-mqtt wrapper
│   │       └── messages/
│   │           └── device_online_message.py   # MQTT payload DTO
│   ├── persistence/
│   │   ├── database/
│   │   │   ├── database.py                    # Database (pool + migrate)
│   │   │   ├── datastore.py                   # DataStore (atomic, query)
│   │   │   └── tx.py                          # Tx wraps psycopg2 cursor
│   │   └── repositories/
│   │       └── device/
│   │           └── postgres_device_repository.py
│   └── runner/
│       └── device_runtime_runner.py           # while True → SendDeviceOnlineUseCase
│
└── presentation/                              # entry points from external world
    └── messaging/
        ├── router.py                          # MessageRouter (topic → handler)
        └── mqtt/
            └── handlers/
                └── register_device_message_handler.py  # parse MQTT → call use case
```
