from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.dependencies.rate_limit import rate_limit

from app.core.redis import redis_client
from app.db.session import get_db


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check():
    return {"status": "ok"}


@router.get("/db")
def db_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}


@router.get("/redis")
def redis_health():
    redis_client.ping()
    return {"redis": "ok"}


@router.get("/limited", dependencies=[Depends(rate_limit(limit=5, window_seconds=60))])
def limited_endpoint():
    return {"message": "ok"}