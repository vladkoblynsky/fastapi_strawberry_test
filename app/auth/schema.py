import strawberry
from fastapi import Response
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.auth.inputs import LoginInput, SignUpInput
from app.auth.types import LoginResult, SignUpResult
from app.auth.utils import verify_password
from app.core.enums import ErrorCode
from app.core.types import ErrorType
from app.schemas import UserCreateSchema
from app.user import crud as user_crud


@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self, info: Info, input_data: LoginInput) -> LoginResult:
        db: Session = info.context['db']
        authorize: AuthJWT = info.context['authorize']
        user = user_crud.get_user_by_email(db, input_data.email)
        if not user or not verify_password(input_data.password, user.hashed_password):
            authorize.unset_jwt_cookies()
            errors = [ErrorType(code=ErrorCode.INVALID_INPUT_DATA, message='Invalid email or password')]
            return LoginResult(user=None, errors=errors, access_token=None, refresh_token=None)

        access_token = authorize.create_access_token(subject=user.email)
        refresh_token = authorize.create_refresh_token(subject=user.email)
        authorize.set_access_cookies(access_token)
        authorize.set_refresh_cookies(refresh_token)
        return LoginResult(user=user, errors=[], access_token=access_token, refresh_token=refresh_token)

    @strawberry.mutation
    def logout(self, info: Info) -> bool:
        authorize: AuthJWT = info.context['authorize']
        authorize.jwt_required()
        authorize.unset_jwt_cookies()
        return True

    @strawberry.mutation
    def refresh(self, info: Info) -> bool:
        authorize: AuthJWT = info.context['authorize']
        authorize.jwt_refresh_token_required()

        current_user = authorize.get_jwt_subject()
        new_access_token = authorize.create_access_token(subject=current_user)
        authorize.set_access_cookies(new_access_token)
        return True

    @strawberry.mutation
    def signup(self, info: Info, input_data: SignUpInput) -> SignUpResult:
        db: Session = info.context['db']
        authorize: AuthJWT = info.context['authorize']
        user_in_db = user_crud.get_user_by_email(db, input_data.email)
        if user_in_db:
            errors = [ErrorType(code=ErrorCode.INVALID_INPUT_DATA, message='User with this email exists')]
            return SignUpResult(user=None, errors=errors)
        user = user_crud.create_user(db, UserCreateSchema(email=input_data.email, password=input_data.password))
        access_token = authorize.create_access_token(subject=user.email)
        refresh_token = authorize.create_refresh_token(subject=user.email)
        authorize.set_access_cookies(access_token)
        authorize.set_refresh_cookies(refresh_token)
        return SignUpResult(user=user, errors=[], access_token=access_token, refresh_token=refresh_token)
