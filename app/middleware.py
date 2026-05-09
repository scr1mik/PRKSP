import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.core.logging import get_logger, request_id_context


async def shutdown_guard_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if getattr(request.app.state, "is_shutting_down", False):
        return JSONResponse(
            status_code=503,
            content={"detail": "Service is shutting down"},
        )
    return await call_next(request)


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = request_id_context.set(request_id)
    start_time = time.perf_counter()
    logger = get_logger()

    try:
        response = await call_next(request)
    except Exception:
        duration_s = round((time.perf_counter() - start_time), 5)
        logger.exception(
            "http_request_failed",
            extra={
                "request_id": request_id,
                "structured": {
                    "method": request.method,
                    "path": request.url.path,
                    "duration_s": duration_s,
                },
            },
        )
        request_id_context.reset(token)
        raise

    duration_s = round((time.perf_counter() - start_time), 5)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "http_request_completed",
        extra={
            "request_id": request_id,
            "structured": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_s": duration_s,
            },
        },
    )
    request_id_context.reset(token)
    return response
