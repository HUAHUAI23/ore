"""
用户管理相关的DTO（Data Transfer Object）模型
遵循2025年FastAPI和Pydantic最佳实践
"""
from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
import re


class UserCreateRequest(BaseModel):
    """用户注册请求DTO"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid',
        json_schema_extra={
            "example": {
                "name": "testuser",
                "password": "password123",
                "nickname": "Test User",
                "email": "user@example.com",
                "phone": "13800138000"
            }
        }
    )
    
    name: Annotated[str, Field(
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="用户名：3-50个字符，只能包含字母、数字、下划线和连字符",
        examples=["testuser", "user_123", "demo-user"]
    )]
    
    password: Annotated[str, Field(
        min_length=6,
        max_length=128,
        description="密码：至少6个字符",
        examples=["password123", "mySecurePass456"]
    )]
    
    nickname: Annotated[Optional[str], Field(
        default=None,
        min_length=1,
        max_length=50,
        description="昵称：1-50个字符，可选",
        examples=["张三", "Test User", "开发者"]
    )] = None
    
    email: Annotated[Optional[EmailStr], Field(
        default=None,
        description="邮箱地址，可选",
        examples=["user@example.com", "test@domain.org"]
    )] = None
    
    phone: Annotated[Optional[str], Field(
        default=None,
        pattern=r'^1[3-9]\d{9}$',
        description="手机号码：中国大陆手机号格式，可选",
        examples=["13800138000", "15912345678"]
    )] = None
    
    @field_validator('name')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """用户名验证"""
        if not v:
            raise ValueError('用户名不能为空')
        
        if v[0].isdigit():
            raise ValueError('用户名不能以数字开头')
        
        reserved_words = ['admin', 'root', 'user', 'test', 'api', 'www', 'mail']
        if v.lower() in reserved_words:
            raise ValueError(f'用户名不能使用保留关键字: {v}')
        
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """密码强度验证"""
        if len(v) < 6:
            raise ValueError('密码至少需要6个字符')
        
        weak_patterns = ['123456', 'password', 'qwerty', '111111']
        if any(pattern in v.lower() for pattern in weak_patterns):
            raise ValueError('密码过于简单，请使用更复杂的密码')
        
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """手机号码验证"""
        if v is None:
            return v
        
        phone_digits = re.sub(r'\D', '', v)
        
        if not re.match(r'^1[3-9]\d{9}$', phone_digits):
            raise ValueError('请输入有效的中国大陆手机号码')
        
        return phone_digits


class UserUpdateRequest(BaseModel):
    """用户信息更新请求DTO"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid',
        json_schema_extra={
            "example": {
                "nickname": "New Nickname",
                "email": "newemail@example.com",
                "phone": "13900139000"
            }
        }
    )
    
    nickname: Annotated[Optional[str], Field(
        default=None,
        min_length=1,
        max_length=50,
        description="昵称：1-50个字符，可选",
        examples=["新昵称", "Updated User"]
    )] = None
    
    email: Annotated[Optional[EmailStr], Field(
        default=None,
        description="邮箱地址，可选",
        examples=["newemail@example.com"]
    )] = None
    
    phone: Annotated[Optional[str], Field(
        default=None,
        pattern=r'^1[3-9]\d{9}$',
        description="手机号码：中国大陆手机号格式，可选",
        examples=["13900139000"]
    )] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """手机号码验证"""
        if v is None:
            return v
        
        phone_digits = re.sub(r'\D', '', v)
        
        if not re.match(r'^1[3-9]\d{9}$', phone_digits):
            raise ValueError('请输入有效的中国大陆手机号码')
        
        return phone_digits


class UserResponse(BaseModel):
    """用户公开信息响应DTO"""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "testuser",
                "nickname": "Test User",
                "email": "user@example.com",
                "phone": "13800138000",
                "is_active": True,
                "created_at": "2025-01-01T00:00:00",
                "last_login": "2025-01-01T12:00:00"
            }
        }
    )
    
    id: Annotated[int, Field(description="用户ID", examples=[1, 123])]
    name: Annotated[str, Field(description="用户名", examples=["testuser", "demo_user"])]
    nickname: Annotated[str, Field(description="昵称", examples=["张三", "Test User"])]
    email: Annotated[Optional[str], Field(description="邮箱地址", examples=["user@example.com"])] = None
    phone: Annotated[Optional[str], Field(description="手机号码", examples=["13800138000"])] = None
    is_active: Annotated[bool, Field(description="是否激活", examples=[True, False])]
    created_at: Annotated[datetime, Field(description="创建时间")]
    last_login: Annotated[Optional[datetime], Field(description="最后登录时间")] = None