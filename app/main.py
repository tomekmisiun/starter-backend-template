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
from app.api.legacy import legacy_api_router
from app.api.openapi import configure_openapi
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.v1 import api_v1_router
from app.core.config import settings

configure_logging()
initialize_error_tracking()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    summary="Reusable FastAPI backend template",
)
configure_openapi(app)

app.add_middleware(RequestContextMiddleware)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(api_v1_router)
app.include_router(legacy_api_router)
