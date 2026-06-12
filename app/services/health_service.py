from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.metrics import observe_dependency_check
from app.core.redis import redis_client
from app.schemas.health import DependencyHealth, ReadinessHealth


def check_database(db: Session) -> DependencyHealth:
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        observe_dependency_check(dependency="database", status="unavailable")
        return DependencyHealth(
            status="unavailable",
            message="database unavailable",
        )

    observe_dependency_check(dependency="database", status="ok")
    return DependencyHealth(status="ok")


def check_redis() -> DependencyHealth:
    try:
        redis_client.ping()
    except Exception:
        observe_dependency_check(dependency="redis", status="unavailable")
        return DependencyHealth(
            status="unavailable",
            message="redis unavailable",
        )

    observe_dependency_check(dependency="redis", status="ok")
    return DependencyHealth(status="ok")


def get_readiness(db: Session) -> ReadinessHealth:
    checks = {
        "database": check_database(db),
        "redis": check_redis(),
    }

    if any(check.status != "ok" for check in checks.values()):
        return ReadinessHealth(status="unavailable", checks=checks)

    return ReadinessHealth(status="ok", checks=checks)
