# Application Config

The config module is responsible for loading and managing application configuration.

This layer contains configuration objects and environment parsing logic used by the infrastructure and application layers.

Typical configuration sources:
- environment variables
- `.env` files
- yaml/json configuration files

The config layer should only focus on:
- reading configuration values
- validating configuration structure
- exposing strongly typed configuration objects

It should NOT:
- create application services
- register dependencies
- perform dependency injection
- bootstrap the application

---

# Files

## config.py

Main configuration entry point.

Responsibilities:
- initialize configuration loading
- aggregate all configuration sections
- expose a single application config object

---

## database.py

Contains database-related configuration.

Examples:
- database host
- port
- username
- password
- connection pool settings

---

## http.py

Contains HTTP server configuration.

Examples:
- host
- port
- timeout
- graceful shutdown period

---

## jwt.py

Contains JWT authentication configuration.

Examples:
- secret key
- expiration time
- signing algorithm

---

## logger.py

Contains logging configuration.

Examples:
- log level
- log format
- output destination
