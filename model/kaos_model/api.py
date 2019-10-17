from dataclasses import dataclass
from dataclasses_json import dataclass_json

from typing import TypeVar, Generic

T = TypeVar('T')


@dataclass_json
@dataclass
class Response(Generic[T]):
    response: T


@dataclass_json
@dataclass
class PagedResponse(Generic[T]):
    page_id: int
    page_count: int
    response: T


@dataclass_json
@dataclass
class Error:
    error_code: str  # fine-grained error type string
    message: str  # detailed explanation of the error
