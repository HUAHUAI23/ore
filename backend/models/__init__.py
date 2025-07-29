"""
Database models for the backend application.
只包含数据库模型，DTO模型在 schemas/ 目录下
"""
from .user import User

__all__ = ["User"]