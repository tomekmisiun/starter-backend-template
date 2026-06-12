import logging
import time

import sentry_sdk
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.ids import uuid7
from app.core.metrics import get_route_path, observe_request
from app.core.request_context import request_id_var


logger = logging.getLogger("app.requests")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        request_id = request.headers.get("X-Request-ID") or str(uuid7())
        request.state.request_id = request_id
        request_id_token = request_id_var.set(request_id)
        sentry_sdk.set_tag("request_id", request_id)

        try:
            logger.info(
                "request_started",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                },
            )

            response = await call_next(request)

            process_time = time.perf_counter() - start_time
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            if request.url.path != "/metrics":
                observe_request(
                    method=request.method,
                    path=get_route_path(request.scope),
                    status_code=response.status_code,
                    duration_seconds=process_time,
                )

            logger.info(
                "request_finished",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time,
                },
            )

            return response
        finally:
            request_id_var.reset(request_id_token)
