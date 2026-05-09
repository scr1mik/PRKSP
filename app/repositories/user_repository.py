from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserCreate


class UserRepository:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        return self.db_session.scalars(query).first()

    def get(self, user_id: int) -> User | None:
        return self.db_session.get(User, user_id)

    def create(self, payload: UserCreate, password_hash: str) -> User:
        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            password_hash=password_hash,
        )
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user
