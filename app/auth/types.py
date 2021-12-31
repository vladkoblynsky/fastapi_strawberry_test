from typing import Optional

import strawberry

from app.core.types import MutationWithErrorsResult
from app.user.types import UserType


# @strawberry.type
# class LoginSuccess:
#     user: UserType
#
#
# @strawberry.type
# class LoginError:
#     message: str


# LoginResult = strawberry.union("LoginResult", types=(LoginSuccess, LoginError))

@strawberry.type
class LoginResult(MutationWithErrorsResult):
    user: Optional[UserType]
    access_token: Optional[str]
    refresh_token: Optional[str]


@strawberry.type
class SignUpResult(MutationWithErrorsResult):
    user: Optional[UserType]
    access_token: Optional[str]
    refresh_token: Optional[str]
