import strawberry

from app.post.resolvers import resolve_post_user
from app.user.types import UserType


@strawberry.type
class PostType:
    id: int
    title: str
    description: str
    author_id: int
    author: UserType = strawberry.field(resolver=resolve_post_user)
