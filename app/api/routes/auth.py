from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.api.dependencies import get_auth_service, get_current_user, get_session_store
from app.core.security import create_session_id
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, UserRead
from app.services.auth_service import AuthService, InvalidCredentialsError, UserAlreadyExistsError
from app.services.session_store import SessionStore

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        return auth_service.register(payload)
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        ) from exc


@router.post("/login", response_model=UserRead)
def login(
    payload: UserLogin,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    session_store: SessionStore = Depends(get_session_store),
) -> User:
    try:
        user = auth_service.authenticate(payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from exc

    session_id = create_session_id()
    settings = request.app.state.settings
    session_store.set_user_id(session_id, user.id, settings.session_ttl_seconds)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=settings.session_ttl_seconds,
    )
    return user


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    session_store: SessionStore = Depends(get_session_store),
) -> Response:
    settings = request.app.state.settings
    session_id = request.cookies.get(settings.session_cookie_name)
    if session_id:
        session_store.delete(session_id)
    response.delete_cookie(settings.session_cookie_name)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
