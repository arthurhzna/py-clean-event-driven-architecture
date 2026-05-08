# Domain Layer

Contains the core business logic and domain rules of the application.

This layer must not depend on:
- frameworks
- databases
- UI
- infrastructure implementations
- external delivery mechanisms

The domain layer should remain pure and focused only on business concepts and rules.

---

# entities/

Represents domain objects that have unique identity and lifecycle.

Examples:
- User
- Order
- Device
- Session

Characteristics:
- has unique identity
- state can change over time
- represents core business objects

---

# value_objects/

Represents domain concepts without identity.

Examples:
- EmailAddress
- Money
- Address
- Coordinates

Characteristics:
- immutable
- compared by value
- usually contains validation and utility logic

---

# services/

Contains domain logic that does not naturally belong to entities or value objects.

Examples:
- pricing calculation
- validation process
- business rule evaluation

Characteristics:
- stateless
- contains pure domain logic
- operates on domain objects

---

# policies/

Contains business rules and decision-making logic.

Examples:
- permission checking
- eligibility rules
- validation rules
- selection criteria

Characteristics:
- pure rule/decision logic
- usually returns boolean or selection result
- no side effects

---

# repositories/

Defines abstraction interfaces for data persistence.

Examples:
- UserRepository
- OrderRepository
- DeviceRepository

Purpose:
- prevents the domain layer from depending directly on databases
- concrete implementations belong to the infrastructure layer

---

# events/

Represents important events that occur inside the domain.

Examples:
- UserCreatedEvent
- OrderCompletedEvent
- DeviceOnlineEvent

Purpose:
- communication between system components
- supports event-driven architecture
- decouples producers and consumers

---

# enums/

Contains domain constants with a limited set of values.

Examples:
- OrderStatus
- PaymentType
- UserRole

Characteristics:
- finite values
- represents status/category/type

---

# exceptions/

Contains custom domain-specific exceptions.

Examples:
- InvalidOrderException
- PaymentFailedException
- UnauthorizedActionException

Purpose:
- represents invalid or abnormal domain conditions
- simplifies domain error handling
