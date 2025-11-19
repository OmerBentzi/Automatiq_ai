"""
Main Application Entry Point
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FastAPI application setup with middleware, CORS, and route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
# Import models FIRST before anything else
from app.models.employee import Employee  # noqa: F401
# Now import routes (which will also import Employee, but it's already defined)
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup: Create tables if they don't exist
    # Note: In production, use Alembic for migrations
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables verified/created")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
    
    yield
    
    # Shutdown: cleanup if needed
    print("👋 Application shutting down")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered cybersecurity training assistant with natural language processing",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix="/api", tags=["Training Assistant"])


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "CyberSecurity Training Assistant API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

