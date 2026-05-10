from __future__ import annotations

from dataclasses import dataclass
from typing import Generic
from typing import TypeVar


T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T
    ok: bool = True

    def is_ok(
        self,
    ) -> bool:
        return True

    def is_err(
        self,
    ) -> bool:
        return False


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E
    ok: bool = False

    def is_ok(
        self,
    ) -> bool:
        return False

    def is_err(
        self,
    ) -> bool:
        return True


Result = Ok[T] | Err[E]