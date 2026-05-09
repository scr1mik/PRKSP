import asyncio
import os
import socket

from fastapi import APIRouter, Query, Request

router = APIRouter()


@router.get("/instance")
def read_instance(request: Request) -> dict[str, str | int]:
    settings = request.app.state.settings
    return {
        "service": settings.app_name,
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
    }


@router.get("/runtime/slow")
async def slow_request(seconds: float = Query(default=5.0, ge=0.0, le=30.0)) -> dict[str, str | float]:
    await asyncio.sleep(seconds)
    return {"status": "completed", "seconds": seconds}
