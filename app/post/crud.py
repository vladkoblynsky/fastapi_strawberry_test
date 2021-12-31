from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app import models, schemas


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    # return db.query(models.Post).options(joinedload(models.Post.author)).offset(skip).limit(limit).all()
    return db.query(models.Post).offset(skip).limit(limit).all()


def create_user_post(db: Session, post: schemas.PostCreateSchema, user_id: int):
    db_post = models.Post(**post.dict(), author_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
