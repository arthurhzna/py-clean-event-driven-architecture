# Application Layer

The application layer contains use cases that orchestrate the flow of the system.

This layer is responsible for:
- coordinating domain objects and services
- executing application-specific workflows
- handling input/output flow between layers
- invoking repositories, domain services, and events

The application layer does not contain infrastructure details such as:
- database implementation
- web framework logic
- external API implementation

It acts as the bridge between the outside world and the domain layer.

---

# usecases/

Contains application use cases representing specific system actions or workflows.

Characteristics:
- orchestrates business operations
- coordinates domain services, entities, repositories, and events
- contains application flow logic
- should remain framework-independent

Examples:
- CreateUserUseCase
- ProcessPaymentUseCase
- AuthenticateUserUseCase
- GenerateReportUseCase
