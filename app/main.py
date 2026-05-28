from fastapi import FastAPI

app = FastAPI(title="Starter Backend Template")


@app.get("/health")
def health_check():
    return {"status": "ok"}