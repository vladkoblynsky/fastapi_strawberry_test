from typing import List, Optional

import strawberry
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.user import crud
from app.user.types import UserType


@strawberry.type
class Query:
    @strawberry.field
    def users(self, info: Info, limit: int = 10) -> List[UserType]:
        db: Session = info.context['db']
        users = crud.get_users(db, limit=limit)
        return users

    @strawberry.field
    def me(self, info: Info) -> Optional[UserType]:
        return info.context['user']
