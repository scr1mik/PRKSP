from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.events import router as events_router
from app.api.routes.instance import router as instance_router
from app.api.routes.release import router as release_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(events_router, prefix="/events", tags=["events"])
api_router.include_router(instance_router, tags=["runtime"])
api_router.include_router(release_router, tags=["release"])
