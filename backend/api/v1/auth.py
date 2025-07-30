"""
Authentication API endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Depends

from backend.core.auth import get_current_user
from backend.db import SessionDep
from backend.models.user import User
from backend.schemas.auth import UserLoginRequest, TokenResponse
from backend.schemas.user import UserCreateRequest, UserResponse
from backend.schemas.common import ApiResponse
from backend.services.auth import AuthService
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(user_data: UserLoginRequest, session: SessionDep):
    """用户登录端点 - 用户名密码验证"""
    try:
        user, access_token = await AuthService.login_user(session, user_data)
        
        # Convert user to public model for response
        user_response = UserResponse.model_validate(user)
        
        token_data = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
        return ApiResponse(message="登录成功", data=token_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.post("/register", response_model=ApiResponse[TokenResponse])
async def register(user_data: UserCreateRequest, session: SessionDep):
    """用户注册端点"""
    try:
        user, access_token = await AuthService.register_user(session, user_data)
        
        # Convert user to public model for response
        user_response = UserResponse.model_validate(user)
        
        token_data = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
        return ApiResponse(message="注册成功", data=token_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.get("/me", response_model=ApiResponse[UserResponse])
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    user_response = UserResponse.model_validate(current_user)
    return ApiResponse(data=user_response)