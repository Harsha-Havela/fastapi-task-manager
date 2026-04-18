from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

from app.core.config import settings
from app.db.session import engine, Base
from app.api.routes import auth, tasks

# Import models so SQLAlchemy registers them before creating tables
import app.models.user  # noqa: F401
import app.models.task  # noqa: F401

# Create all tables on startup
Base.metadata.create_all(bind=engine)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

app = FastAPI(
    title=settings.APP_NAME,
    description="A simple Task Manager REST API built with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS – allow all origins for development; tighten in production via env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth & task routes
app.include_router(auth.router)
app.include_router(tasks.router)

# Frontend route - serves the main application
@app.get("/", include_in_schema=False)
def serve_frontend(request: Request):
    """Serve the main frontend application"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
