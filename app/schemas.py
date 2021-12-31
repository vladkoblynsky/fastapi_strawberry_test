from typing import List, Optional

from pydantic import BaseModel


class PostBaseSchema(BaseModel):
    title: str
    description: Optional[str] = None


class PostCreateSchema(PostBaseSchema):
    pass


class PostSchema(PostBaseSchema):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBaseSchema(BaseModel):
    email: str


class UserCreateSchema(UserBaseSchema):
    password: str


class UserSchema(UserBaseSchema):
    id: int
    is_active: bool
    posts: List[PostSchema] = []

    class Config:
        orm_mode = True
