import strawberry


@strawberry.type
class UserType:
    id: int
    email: str
    is_active: bool
