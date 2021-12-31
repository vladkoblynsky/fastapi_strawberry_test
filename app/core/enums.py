from enum import Enum
import strawberry


@strawberry.enum
class ErrorCode(Enum):
    INVALID_INPUT_DATA = 'invalid_input_data'
