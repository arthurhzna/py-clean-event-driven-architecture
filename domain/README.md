# Domain Layer

Contains the core business logic and domain rules of the application.
This layer must not depend on frameworks, databases, UI, or external libraries.

---

# entities/

Represents domain objects that have unique identity and lifecycle.

Examples:
- TrackedPerson
- Alert
- CameraSession

Characteristics:
- has unique identity
- state can change over time
- represents core business objects

---

# value_objects/

Represents domain concepts without identity.

Examples:
- BoundingBox
- Detection
- ConfidenceScore
- PolygonArea

Characteristics:
- immutable
- compared by value
- usually contains validation and utility logic

---

# services/

Contains domain logic that does not naturally belong to entities or value objects.

Examples:
- tracking process
- face recognition analysis
- behavior analysis

Characteristics:
- stateless
- orchestrates domain processes
- contains pure domain logic

---

# policies/

Contains business rules and decision-making logic.

Examples:
- confidence threshold
- restricted area checking
- disappear condition

Characteristics:
- pure rule/decision logic
- usually returns boolean or selection result
- no side effects

---

# repositories/

Defines abstraction interfaces for data persistence.

Examples:
- PersonRepository
- AlertRepository

Purpose:
- prevents the domain layer from depending directly on databases
- concrete implementations belong to the infrastructure layer

---

# events/

Represents important events that occur inside the domain.

Examples:
- PersonDetectedEvent
- DrowsinessEvent
- RestrictedAreaEvent

Purpose:
- communication between system components
- supports event-driven architecture
- decouples producers and consumers

---

# enums/

Contains domain constants with a limited set of values.

Examples:
- AttentionState
- BehaviorType

Characteristics:
- finite values
- represents status/category/type

---

# exceptions/

Contains custom domain-specific exceptions.

Examples:
- InvalidBBoxException
- DetectionException

Purpose:
- represents invalid or abnormal domain conditions
- simplifies domain error handling
