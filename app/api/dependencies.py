from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.session_store import SessionStore


def get_auth_service(db_session: Session = Depends(get_db_session)) -> AuthService:
    return AuthService(UserRepository(db_session))


def get_session_store(request: Request) -> SessionStore:
    return request.app.state.session_store


def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    session_store: SessionStore = Depends(get_session_store),
) -> User:
    app_settings = request.app.state.settings
    session_id = request.cookies.get(app_settings.session_cookie_name)
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    user_id = session_store.get_user_id(session_id)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    user = auth_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
