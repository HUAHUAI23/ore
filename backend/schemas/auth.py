"""
认证相关的DTO（Data Transfer Object）模型
遵循2025年FastAPI和Pydantic最佳实践
"""
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict

from .user import UserResponse


class UserLoginRequest(BaseModel):
    """用户登录请求DTO"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid',
        json_schema_extra={
            "example": {
                "name": "testuser",
                "password": "password123"
            }
        }
    )
    
    name: Annotated[str, Field(
        min_length=1,
        max_length=50,
        description="用户名或邮箱",
        examples=["testuser", "user@example.com"]
    )]
    
    password: Annotated[str, Field(
        min_length=1,
        max_length=128,
        description="密码",
        examples=["password123"]
    )]


class TokenResponse(BaseModel):
    """Token响应DTO"""
    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "name": "testuser",
                    "nickname": "Test User",
                    "email": "user@example.com",
                    "phone": None,
                    "is_active": True,
                    "created_at": "2025-01-01T00:00:00",
                    "last_login": "2025-01-01T12:00:00"
                }
            }
        }
    )
    
    access_token: Annotated[str, Field(
        description="JWT访问令牌",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )]
    
    token_type: Annotated[str, Field(
        description="令牌类型",
        examples=["bearer"]
    )] = "bearer"
    
    expires_in: Annotated[int, Field(
        description="过期时间（秒）",
        examples=[1800, 3600, 7200]
    )] = 1800
    
    user: Annotated[UserResponse, Field(
        description="用户信息"
    )]


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求DTO"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid',
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )
    
    refresh_token: Annotated[str, Field(
        min_length=1,
        description="刷新令牌",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )]


class PasswordChangeRequest(BaseModel):
    """修改密码请求DTO"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid',
        json_schema_extra={
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        }
    )
    
    current_password: Annotated[str, Field(
        min_length=1,
        max_length=128,
        description="当前密码",
        examples=["oldpassword123"]
    )]
    
    new_password: Annotated[str, Field(
        min_length=6,
        max_length=128,
        description="新密码：至少6个字符",
        examples=["newpassword456"]
    )]