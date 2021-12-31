from typing import List

from strawberry.dataloader import DataLoader

from app.database import SessionLocal
from app.models import User
from app.user.crud import get_users_by_ids


async def load_users(keys) -> List[User]:
    db = SessionLocal()
    users = get_users_by_ids(db, keys)
    qs = {}
    for user in users:
        qs[user.id] = user
    return [qs[key] for key in keys]


loader = {
    "users_by_id": DataLoader(load_fn=load_users)
}
