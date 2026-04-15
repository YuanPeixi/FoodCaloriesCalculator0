"""Food Calories Calculator — FastAPI application.

A web application that identifies food and estimates calories from photos.
Supports:
- Single photo recognition
- Before/after meal photo comparison for accurate portion estimation
- OpenRouter multi-modal models (e.g. Qwen2.5-VL)
- Self-trained local models (placeholder with training documentation)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .routers import food

app = FastAPI(
    title="Food Calories Calculator",
    description="Identify food and estimate calories from photos",
    version="1.0.0",
)

# CORS — allow the frontend (served separately or from the same origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(food.router)

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
frontend_dir = os.path.abspath(frontend_dir)

if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_frontend():
        """Serve the frontend index.html."""
        return FileResponse(os.path.join(frontend_dir, "index.html"))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Food Calories Calculator"}
