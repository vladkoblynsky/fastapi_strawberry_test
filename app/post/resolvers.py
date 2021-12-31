from strawberry.types import Info

from app.user.types import UserType


async def resolve_post_user(root, info: Info) -> UserType:
    return await info.context['loader']['users_by_id'].load(root.author_id)