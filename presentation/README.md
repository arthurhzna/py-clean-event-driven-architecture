# Presentation Layer

The `presentation` layer acts as the application's entry point.

Its responsibility is to:

* receive external input
* parse requests/messages
* validate transport-level data
* invoke application use cases

This layer must **NOT** contain:

* business rules
* domain logic
* infrastructure implementation details
* direct state mutation logic

---

# Structure

```txt
presentation/
├── http/
└── messaging/
```

---

# presentation/http

Contains HTTP adapters such as:

* FastAPI routes
* Flask controllers
* REST endpoints
* WebSocket handlers

Example responsibility:

```python
@app.post("/analyze")
def analyze():

    result = analyze_person_uc.execute()

    return result
```

The HTTP layer should only:

1. receive HTTP requests
2. transform request data
3. call use cases
4. return HTTP responses

Business logic must remain inside the application/domain layers.

---

# presentation/messaging

Contains message-based adapters such as:

* MQTT consumers
* Kafka consumers
* RabbitMQ subscribers

Example responsibility:

```python
def on_message(payload):

    analyze_person_uc.execute(payload)
```

The messaging layer should only:

1. receive external messages/events
2. deserialize payloads
3. invoke use cases

It should NOT:

* directly mutate domain state
* directly call repositories
* directly implement business rules

---

# Important Rule

Presentation adapters must always communicate through:

```txt
Presentation
    ↓
Application UseCase
    ↓
Domain
```

and NOT:

```txt
Presentation
    ↓
Direct Domain Mutation
```

This keeps:

* business flow centralized
* architecture maintainable
* event-driven workflows consistent
* runtime adapters thin and simple

```
```
