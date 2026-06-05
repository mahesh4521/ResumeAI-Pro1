from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import resume_router, role_router
import uvicorn
import logging
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ResumeAI Pro API",
    description="Intelligent Career Acceleration Platform - AI-powered resume analysis and career guidance",
    version="1.0.0"
)

# CORS middleware
allowed_origins = [
    "http://localhost:3006", 
    "http://127.0.0.1:3006",
    "http://77.37.45.138:3006"
]
env_origins = os.getenv("ALLOWED_ORIGINS")
if env_origins:
    allowed_origins = [o.strip() for o in env_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(resume_router.router)
app.include_router(role_router.router)

@app.get("/api")
async def api_root():
    return {
        "message": "ResumeAI Pro API",
        "description": "Intelligent Career Acceleration Platform",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "resume": "/resume", 
            "roles": "/roles",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ResumeAI Pro"}

# ---------- Serve React Frontend ----------
# Path to the React production build
FRONTEND_BUILD_DIR = Path(__file__).parent / "frontend" / "build"

if FRONTEND_BUILD_DIR.exists():
    # Serve static assets (JS, CSS, images, etc.)
    app.mount("/static", StaticFiles(directory=FRONTEND_BUILD_DIR / "static"), name="static")

    # Catch-all route: serve React's index.html for any non-API route
    # This enables React Router client-side routing
    @app.get("/{full_path:path}")
    async def serve_react(request: Request, full_path: str):
        # If the requested file exists in the build folder, serve it (favicon, manifest, etc.)
        file_path = FRONTEND_BUILD_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        # Otherwise serve index.html for React Router
        return FileResponse(FRONTEND_BUILD_DIR / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "message": "ResumeAI Pro API",
            "description": "Frontend build not found. Run the build script first.",
            "docs": "/docs"
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8006))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )