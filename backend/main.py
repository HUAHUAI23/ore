from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time

from backend.core.config import settings
from backend.utils.logger import get_logger
from backend.utils.exceptions import (
    CustomHTTPException,
    BusinessException,
    custom_http_exception_handler,
    business_exception_handler,
    general_exception_handler,
)
from backend.schemas.common import HealthCheck, ApiResponse
from backend.api.v1 import auth

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize database tables
    try:
        from backend.db import create_db_and_tables

        await create_db_and_tables()
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        # 在开发环境中，可以选择继续运行，但在生产环境中可能需要停止
        if settings.environment == "production":
            raise
        else:
            logger.warning("⚠️  Continuing in development mode despite database error")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")
    try:
        from backend.db import engine

        await engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {process_time:.4f}s")
    return response


# Exception handlers
app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# Health check endpoint
@app.get("/health", response_model=ApiResponse[HealthCheck], tags=["Health"])
async def health_check():
    """Health check endpoint"""
    health_data = HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=settings.app_version,
    )
    return ApiResponse(data=health_data)


# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
