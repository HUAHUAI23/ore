"""
工作流执行API端点
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query

from backend.core.auth import get_current_user
from backend.db import SessionDep
from backend.models.user import User
from backend.schemas.workflow import (
    WorkflowExecutionResponse,
    WorkflowExecutionListItem,
)
from backend.schemas.common import ApiResponse, PaginatedResponse
from backend.services.workflow_execution import WorkflowExecutionService
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/workflows", tags=["workflow-executions"])


@router.get(
    "/{workflow_id}/executions",
    response_model=ApiResponse[PaginatedResponse[WorkflowExecutionListItem]],
)
async def list_workflow_executions(
    workflow_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="限制返回数量"),
):
    """获取工作流执行历史列表"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="用户未认证"
            )

        executions, total = await WorkflowExecutionService.get_workflow_executions(
            session, workflow_id, current_user.id, skip, limit
        )

        execution_items = [
            WorkflowExecutionListItem.model_validate(ex) for ex in executions
        ]

        paginated_response = PaginatedResponse(
            items=execution_items, total=total, skip=skip, limit=limit
        )

        return ApiResponse(data=paginated_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List executions for workflow {workflow_id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取执行历史失败"
        )


@router.get(
    "/executions/{execution_id}", response_model=ApiResponse[WorkflowExecutionResponse]
)
async def get_execution_detail(
    execution_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """获取工作流执行详情"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="用户未认证"
            )

        execution = await WorkflowExecutionService.get_execution_by_id(
            session, execution_id, current_user.id
        )

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="执行记录不存在或无权限访问",
            )

        execution_response = WorkflowExecutionResponse.model_validate(execution)
        return ApiResponse(data=execution_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get execution {execution_id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取执行详情失败"
        )


@router.post("/executions/{execution_id}/cancel", response_model=ApiResponse[None])
async def cancel_execution(
    execution_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """取消工作流执行"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="用户未认证"
            )

        success = await WorkflowExecutionService.cancel_execution(
            session, execution_id, current_user.id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="执行记录不存在或无权限访问",
            )

        return ApiResponse(message="工作流执行已取消")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel execution {execution_id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="取消执行失败"
        )


@router.post(
    "/{workflow_id}/run", response_model=ApiResponse[WorkflowExecutionResponse]
)
async def run_workflow(
    workflow_id: int,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """运行工作流"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="用户未认证"
            )

        # 创建执行记录
        execution = await WorkflowExecutionService.create_execution(
            session, workflow_id, current_user.id
        )

        # 立即启动执行
        if execution.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="执行记录创建失败",
            )

        execution = await WorkflowExecutionService.start_workflow_execution(
            session, execution.id, current_user.id
        )

        execution_response = WorkflowExecutionResponse.model_validate(execution)
        return ApiResponse(message="工作流已开始运行", data=execution_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Run workflow {workflow_id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="运行工作流失败"
        )
