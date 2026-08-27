"""
CyberMentor FastAPI Application

Entry point for the backend API server. Configures CORS, mounts routes,
serves the frontend static files, and provides a health check endpoint.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes.chat import router as chat_router
from api.routes.progress import router as progress_router
from api.models import HealthResponse

# Load environment variables
load_dotenv()

# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CyberMentor API",
    description="AI Career Coach for Aspiring Cybersecurity Professionals",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(chat_router)
app.include_router(progress_router)


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Cloud Run and load balancers."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/")
async def root():
    """Serve the frontend index.html."""
    web_dir = Path(__file__).parent.parent / "web"
    index = web_dir / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "CyberMentor API is running. Visit /docs for API documentation."}


# ── Static Files (Frontend) ───────────────────────────────────────────────────
web_dir = Path(__file__).parent.parent / "web"
if web_dir.exists():
    app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="static")
