from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
)
from app.core.error_tracking import initialize_error_tracking
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.core.config import settings
from app.api.routes import users

configure_logging()
initialize_error_tracking()

app = FastAPI(title=settings.app_name)

app.add_middleware(RequestContextMiddleware)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(auth_router)
app.include_router(files_router)
app.include_router(admin_router)
app.include_router(users.router)
