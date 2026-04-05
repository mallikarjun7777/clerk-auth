from sqlalchemy.orm import Session

from database.models import User


def get_user_by_clerk_id(db: Session, clerk_id: str) -> User | None:
    return db.query(User).filter(User.clerk_id == clerk_id).first()


def create_user(db: Session, clerk_id: str, email: str) -> User:
    user = User(clerk_id=clerk_id, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_user(db: Session, clerk_id: str, email: str) -> User:
    existing = get_user_by_clerk_id(db, clerk_id)
    if existing:
        return existing
    return create_user(db, clerk_id, email)
