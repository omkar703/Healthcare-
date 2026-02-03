from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db

# Import routers (will be created later)
# from app.api.v1 import patients, doctors, documents, chat, rag

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="HIPAA-compliant Healthcare AI Microservice Backend",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(f"👋 {settings.APP_NAME} shutting down")


# ==================== API ROUTERS ====================

from app.api.v1 import patients, doctors, rag, ocr

app.include_router(patients.router, prefix="/api/v1")
app.include_router(doctors.router, prefix="/api/v1")
app.include_router(rag.router, prefix="/api/v1")
app.include_router(ocr.router, prefix="/api/v1")


# ==================== HEALTH CHECK ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Include routers (will be uncommented as we create them)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
