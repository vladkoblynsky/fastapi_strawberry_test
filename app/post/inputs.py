import strawberry


@strawberry.input
class PostInput:
    title: str
    description: str
