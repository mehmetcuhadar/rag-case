from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes.health import router as health_router
from app.api.routes.chats import router as chats_router
from app.api.routes.auth import router as auth_router

def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title=settings.APP_NAME)

    app.include_router(health_router)
    app.include_router(chats_router)
    app.include_router(auth_router)
    return app


app = create_app()