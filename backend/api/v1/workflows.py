"""
工作流管理API端点
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Query

from backend.core.auth import get_current_user
from backend.db import SessionDep
from backend.models.user import User
from backend.models.workflow import WorkflowStatus
from backend.schemas.workflow import (
    WorkflowCreateRequest,
    WorkflowUpdateRequest, 
    WorkflowResponse,
    WorkflowListItem
)
from backend.schemas.common import ApiResponse, PaginatedResponse
from backend.services.workflow import WorkflowService
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", response_model=ApiResponse[WorkflowResponse])
async def create_workflow(
    workflow_data: WorkflowCreateRequest,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """创建新工作流"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户未认证"
            )
        
        workflow = await WorkflowService.create_workflow(
            session, workflow_data, current_user.id
        )
        
        workflow_response = WorkflowResponse.model_validate(workflow)
        return ApiResponse(message="工作流创建成功", data=workflow_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create workflow failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建工作流失败"
        )


@router.get("", response_model=ApiResponse[PaginatedResponse[WorkflowListItem]])
async def list_workflows(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="限制返回数量"),
    status_filter: Optional[WorkflowStatus] = Query(None, description="状态过滤")
):
    """获取用户工作流列表"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户未认证"
            )
        
        workflows, total = await WorkflowService.get_user_workflows(
            session, current_user.id, skip, limit, status_filter
        )
        
        workflow_items = [WorkflowListItem.model_validate(wf) for wf in workflows]
        
        paginated_response = PaginatedResponse(
            items=workflow_items,
            total=total,
            skip=skip,
            limit=limit
        )
        
        return ApiResponse(data=paginated_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List workflows failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取工作流列表失败"
        )


@router.get("/{workflow_id}", response_model=ApiResponse[WorkflowResponse])
async def get_workflow(
    workflow_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """获取工作流详情"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户未认证"
            )
        
        workflow = await WorkflowService.get_workflow_by_id(
            session, workflow_id, current_user.id
        )
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流不存在或无权限访问"
            )
        
        workflow_response = WorkflowResponse.model_validate(workflow)
        return ApiResponse(data=workflow_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workflow {workflow_id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取工作流详情失败"
        )


@router.put("/{workflow_id}", response_model=ApiResponse[WorkflowResponse])
async def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowUpdateRequest,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """更新工作流"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户未认证"
            )
        
        workflow = await WorkflowService.update_workflow(
            session, workflow_id, workflow_data, current_user.id
        )
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流不存在或无权限访问"
            )
        
        workflow_response = WorkflowResponse.model_validate(workflow)
        return ApiResponse(message="工作流更新成功", data=workflow_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update workflow {workflow_id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新工作流失败"
        )


@router.delete("/{workflow_id}", response_model=ApiResponse[None])
async def delete_workflow(
    workflow_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user)
):
    """删除工作流（软删除）"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户未认证"
            )
        
        success = await WorkflowService.delete_workflow(
            session, workflow_id, current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作流不存在或无权限访问"
            )
        
        return ApiResponse(message="工作流删除成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete workflow {workflow_id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除工作流失败"
        )