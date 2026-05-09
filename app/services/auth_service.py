from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def register(self, payload: UserCreate) -> User:
        if self.repository.get_by_email(payload.email.lower()) is not None:
            raise UserAlreadyExistsError

        return self.repository.create(payload, hash_password(payload.password))

    def authenticate(self, email: str, password: str) -> User:
        user = self.repository.get_by_email(email.lower())
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError
        return user

    def get_user(self, user_id: int) -> User | None:
        return self.repository.get(user_id)
