from fastapi import FastAPI

from app.api.routes.health import router as health_router


app = FastAPI(title="Starter Backend Template")

app.include_router(health_router)