import uvicorn
from app.core.config import settings


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        access_log=False,
        log_config=None,
    )


if __name__ == "__main__":
    main()
