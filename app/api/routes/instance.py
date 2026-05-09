import os
import socket

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/instance")
def read_instance(request: Request) -> dict[str, str | int]:
    settings = request.app.state.settings
    return {
        "service": settings.app_name,
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
    }
