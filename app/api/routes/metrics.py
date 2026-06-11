from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.core.metrics import render_metrics


router = APIRouter(tags=["metrics"])


@router.get(
    "/metrics",
    response_class=PlainTextResponse,
    summary="Prometheus metrics",
    description="Exposes request counters and latency histograms in Prometheus text format.",
)
def metrics():
    return PlainTextResponse(
        render_metrics(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
