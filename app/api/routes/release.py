from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/release")
def read_release(request: Request) -> dict[str, str]:
    settings = request.app.state.settings
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "image_tag": settings.image_tag,
        "release_id": settings.release_id,
    }
