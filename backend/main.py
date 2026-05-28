import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.detection import router as detection_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.qa import router as qa_router
from app.utils.file_utils import ensure_directories
from app.database import engine, Base

# ---------------------------------------------------------------------------
# Logging setup — must happen before any module imports that use logging
# ---------------------------------------------------------------------------
from app.core.logging_utils import setup_logging, add_request_logging

logger = setup_logging(
    level="DEBUG" if settings.DEBUG else "INFO",
    log_file="app.log",
    log_format="text",
    use_colors="auto",
)

# ---------------------------------------------------------------------------
# Directory bootstrap
# ---------------------------------------------------------------------------
ensure_directories()

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="遥感目标检测平台后端API",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging (adds x-request-id header and latency metrics)
add_request_logging(app, skip_paths={"/health", "/api/test/connect", "/"})

# Static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# API routers
app.include_router(detection_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(qa_router, prefix="/api")
logger.info("Routers registered: detection, auth, users, qa")

# 数据库初始化
@app.on_event("startup")
async def init_database():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/test/connect")
async def test_connect():
    return {"code": 200, "message": "前后端连通成功！"}


# ---------------------------------------------------------------------------
# Lifecycle events
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("🚀 %s v%s starting up", settings.APP_NAME, settings.APP_VERSION)
    logger.info("📁 Static dir  : %s", settings.STATIC_DIR)
    logger.info("📁 Upload dir  : %s", settings.UPLOAD_DIR)
    logger.info("📁 Result dir  : %s", settings.RESULT_DIR)
    logger.info("🤖 Model path  : %s", settings.SEGMENTATION_MODEL_PATH)
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 %s shutting down", settings.APP_NAME)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
