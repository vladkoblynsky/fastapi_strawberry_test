import strawberry


@strawberry.input
class LoginInput:
    email: str
    password: str


@strawberry.input
class SignUpInput:
    email: str
    password: str
