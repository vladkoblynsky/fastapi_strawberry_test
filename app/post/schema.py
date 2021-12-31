from typing import List

import strawberry
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.post.inputs import PostInput
from app.post.types import PostType
from . import crud as post_crud
from ..schemas import PostCreateSchema


@strawberry.type
class Query:

    @strawberry.field
    def posts(self, info: Info, limit: int = 10) -> List[PostType]:
        db: Session = info.context['db']
        posts = post_crud.get_posts(db, limit=limit)
        return posts


@strawberry.type
class Mutation:

    @strawberry.mutation
    def create_post(self, info: Info, input_data: PostInput) -> PostType:
        db: Session = info.context['db']
        user = info.context['user']
        if not user:
            raise Exception("User does not exists")
        post = post_crud.create_user_post(
            db,
            PostCreateSchema(title=input_data.title, description=input_data.description),
            user.id
        )
        return post
