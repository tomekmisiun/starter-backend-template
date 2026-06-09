from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.dependencies.rate_limit import rate_limit
from app.db.session import get_db
from app.schemas.health import HealthStatus, ReadinessHealth
from app.services.health_service import check_database, check_redis, get_readiness


router = APIRouter(prefix="/health", tags=["health"])


def readiness_response(health: ReadinessHealth):
    if health.status == "ok":
        return health

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=health.model_dump(exclude_none=True),
    )


@router.get("", response_model=HealthStatus)
def health_check():
    return HealthStatus(status="ok")


@router.get("/live", response_model=HealthStatus)
def liveness_check():
    return HealthStatus(status="ok")


@router.get(
    "/ready",
    response_model=ReadinessHealth,
    response_model_exclude_none=True,
)
def readiness_check(db: Session = Depends(get_db)):
    return readiness_response(get_readiness(db))


@router.get(
    "/db",
    response_model=ReadinessHealth,
    response_model_exclude_none=True,
)
def db_health_check(db: Session = Depends(get_db)):
    database_check = check_database(db)
    return readiness_response(
        ReadinessHealth(
            status=database_check.status,
            checks={"database": database_check},
        )
    )


@router.get(
    "/redis",
    response_model=ReadinessHealth,
    response_model_exclude_none=True,
)
def redis_health():
    redis_check = check_redis()
    return readiness_response(
        ReadinessHealth(
            status=redis_check.status,
            checks={"redis": redis_check},
        )
    )


@router.get("/limited", dependencies=[Depends(rate_limit(limit=5, window_seconds=60))])
def limited_endpoint():
    return {"message": "ok"}
