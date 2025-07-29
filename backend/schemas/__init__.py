"""
Schemas package for ORE workflow engine backend.

Contains all Pydantic models for request/response validation and documentation.
按功能领域组织，便于维护和扩展。
"""

# Authentication related schemas
from .auth import (
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordChangeRequest,
)

# User management schemas
from .user import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
)

# Common response schemas
from .common import (
    ApiResponse,
    ErrorResponse,
    PaginationMeta,
    PaginatedResponse,
    HealthCheck,
)

__all__ = [
    # Auth schemas
    "UserLoginRequest",
    "TokenResponse", 
    "RefreshTokenRequest",
    "PasswordChangeRequest",
    # User schemas
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserResponse",
    # Common schemas
    "ApiResponse",
    "ErrorResponse",
    "PaginationMeta",
    "PaginatedResponse",
    "HealthCheck",
]