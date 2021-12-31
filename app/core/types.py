import strawberry
from typing import List

from app.core.enums import ErrorCode


@strawberry.type
class ErrorType:
    code: ErrorCode
    message: str


@strawberry.type
class MutationWithErrorsResult:
    errors: List[ErrorType]
