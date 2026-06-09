from fastapi import FastAPI

from app.core.middleware import RequestContextMiddleware
from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.api.routes import users

app = FastAPI(title=settings.app_name)

app.add_middleware(RequestContextMiddleware)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(users.router)
