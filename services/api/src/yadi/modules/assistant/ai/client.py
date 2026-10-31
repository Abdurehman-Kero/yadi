"""The interface the application uses for AI. Nothing outside this package knows the provider."""

from dataclasses import dataclass
from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AiError(Exception):
    """kind: timeout, connection, rate_limited, auth, provider, refused, truncated or
    invalid_output."""

    def __init__(self, kind: str) -> None:
        super().__init__(kind)
        self.kind = kind


@dataclass(frozen=True)
class LlmResult[T]:
    output: T
    model: str
    input_tokens: int
    output_tokens: int


class LlmClient(Protocol):
    model: str

    def generate_structured(self, *, schema: type[T], system: str, prompt: str) -> LlmResult[T]:
        """Returns output validated against `schema`, or raises AiError."""
        ...
