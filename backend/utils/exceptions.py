from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Any


class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str | None = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class BusinessException(Exception):
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


async def custom_http_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, CustomHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "error_code": exc.error_code or "HTTP_ERROR",
                "details": None
            }
        )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "HTTP_ERROR",
            "details": None
        }
    )


async def business_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, BusinessException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": exc.message,
                "error_code": exc.error_code,
                "details": None
            }
        )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "BUSINESS_ERROR",
            "details": None
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "details": str(exc) if hasattr(exc, 'detail') else None
        }
    )