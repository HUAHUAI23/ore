from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    error_code: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    details: Optional[Any] = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
    
    @property
    def page(self) -> int:
        return (self.skip // self.limit) + 1
    
    @property
    def total_pages(self) -> int:
        return (self.total + self.limit - 1) // self.limit


class HealthCheck(BaseModel):
    status: str = "healthy"
    timestamp: str
    version: str