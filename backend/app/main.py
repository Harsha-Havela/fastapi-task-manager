from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

from app.core.config import settings
from app.db.session import engine, Base
from app.api.routes import auth, tasks

# Import models so SQLAlchemy registers them before creating tables
import app.models.user  # noqa: F401
import app.models.task  # noqa: F401

# Create all tables on startup
Base.metadata.create_all(bind=engine)

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

# Simple root endpoint to serve frontend content
@app.get("/", include_in_schema=False)
def serve_frontend():
    # For now, let's serve a simple HTML response
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Task Manager</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { text-align: center; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 FastAPI Task Manager</h1>
            <p>Your Task Manager is successfully deployed!</p>
            <div>
                <a href="/docs" class="btn">📚 API Documentation</a>
                <a href="/redoc" class="btn">📖 ReDoc</a>
            </div>
            <h2>API Endpoints:</h2>
            <ul style="text-align: left;">
                <li><strong>POST /register</strong> - Register a new user</li>
                <li><strong>POST /login</strong> - Login and get JWT token</li>
                <li><strong>GET /tasks</strong> - Get all tasks (requires auth)</li>
                <li><strong>POST /tasks</strong> - Create a task (requires auth)</li>
                <li><strong>PUT /tasks/{id}</strong> - Update a task (requires auth)</li>
                <li><strong>DELETE /tasks/{id}</strong> - Delete a task (requires auth)</li>
            </ul>
            <p><strong>Your API is ready for testing!</strong></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
