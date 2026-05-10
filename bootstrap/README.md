# Application Bootstrap

The bootstrap module is responsible for assembling and wiring the entire application.

This layer acts as the application's composition root.

Responsibilities:
- creating dependencies
- wiring services and use cases
- registering event handlers
- configuring message routing
- initializing the event bus
- connecting infrastructure implementations to abstractions

The bootstrap layer is allowed to import from all layers because it exists at the outermost boundary of the system.

---

# Files

## application.py

Main application bootstrap entry point.

Responsibilities:
- initialize the complete application
- connect all major components together
- create the final application object/container

---

## container.py

Application dependency holder shared by bootstrap factories.

---

## database.py

Creates the database adapter and connection pool from runtime config.

---

## event_bus.py

Responsible for configuring and registering the event bus.

Responsibilities:
- create event bus instance
- register event subscriptions
- connect events to handlers

Examples:
- subscribe event handlers
- configure publish/subscribe flow

---

## message_router.py

Responsible for configuring message routing.

Responsibilities:
- register message handlers
- configure route dispatching
- connect incoming messages to consumers

Examples:
- websocket routing
- kafka topic routing
- queue message routing

---

## mqtt.py

Creates the MQTT client adapter from runtime config.

---

## services.py

Responsible for creating and wiring domain/application services.

Responsibilities:
- instantiate services
- inject dependencies into services
- expose reusable service factories

Examples:
- tracking service
- notification service
- analysis service

---

## usecase_factories/

Responsible for creating and wiring application use cases.

Responsibilities:
- instantiate use cases
- inject repositories and services
- connect use cases with infrastructure components

Examples:
- authentication use case
- processing workflow use case
- event publishing use case
