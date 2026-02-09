from fastapi import FastAPI

from src.backend.app.api.routes import router as api_router

app = FastAPI(title="Vision Enhance Platform", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router)
