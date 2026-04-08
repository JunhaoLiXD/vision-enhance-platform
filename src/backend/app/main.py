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
from fastapi.middleware.cors import CORSMiddleware

from src.backend.app.api.routes import router as api_router

app = FastAPI(title="Vision Enhance Platform", version="0.1.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://vision-enhance-platform.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router)
