"""
Application entry point for the Vision Enhance Platform backend.

Responsibilities:
- Create and configure the FastAPI application instance.
- Register API routers.
- Serve as the startup module for Uvicorn.

Notes:
- Contains no business logic.
- Only responsible for application bootstrapping.
"""
from fastapi import FastAPI

from src.backend.app.api.routes import router as api_router

app = FastAPI(title="Vision Enhance Platform", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router)
