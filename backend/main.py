from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import time
from pathlib import Path
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
from backend.api.v1 import auth, workflows, workflow_executions

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Check database connection
    try:
        from backend.db import engine

        async with engine.connect() as _:
            logger.info("✅ Database connection successful.")
    except Exception as e:
        logger.error(f"❌ Failed to connect to the database: {e}")
        raise

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
app.include_router(workflows.router, prefix="/api/v1", tags=["Workflows"])
app.include_router(
    workflow_executions.router, prefix="/api/v1", tags=["Workflow Executions"]
)

# Static files configuration
if settings.is_development:
    FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"
else:
    FRONTEND_DIR = Path(__file__).parent / "web" / "dist"

# Mount static files for assets (CSS, JS, images, etc.)
if FRONTEND_DIR.exists():
    # app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    # Serve specific static files
    @app.get("/favicon.ico")
    async def get_favicon():
        favicon_path = FRONTEND_DIR / "favicon.ico"
        if favicon_path.exists():
            return FileResponse(favicon_path)
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/manifest.json")
    async def get_manifest():
        manifest_path = FRONTEND_DIR / "manifest.json"
        if manifest_path.exists():
            return FileResponse(manifest_path)
        return FileResponse(FRONTEND_DIR / "index.html")

    # Catch-all route for React SPA - must be last
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Serve React SPA for all non-API routes.
        This handles client-side routing by returning index.html for all paths
        that don't match API endpoints or static files.
        """
        # Skip API routes
        if (
            full_path.startswith("api/")
            or full_path.startswith("docs")
            or full_path.startswith("redoc")
            or full_path.startswith("health")
        ):
            return None

        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        # Fallback if frontend not built
        return {
            "message": "Frontend not found. Please build the frontend first using 'cd frontend && bun run build'"
        }

else:
    logger.warning(
        "⚠️  Frontend dist directory not found. Please build the frontend first."
    )

    @app.get("/{full_path:path}")
    async def frontend_not_built(full_path: str):
        if (
            full_path.startswith("api/")
            or full_path.startswith("docs")
            or full_path.startswith("redoc")
            or full_path.startswith("health")
        ):
            return None
        return {
            "message": "Frontend not built. Please run 'cd frontend && bun run build' first."
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
