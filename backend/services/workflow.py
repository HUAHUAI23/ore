"""
工作流服务层 - 处理工作流CRUD操作和数据库交互
"""

from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, asc, and_, or_, ColumnElement
from sqlmodel import select, func
from fastapi import HTTPException, status

from backend.models.workflow import Workflow, WorkflowStatus
from backend.schemas.workflow import WorkflowCreateRequest, WorkflowUpdateRequest
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class WorkflowService:
    """工作流服务类 - 提供工作流CRUD操作"""

    @staticmethod
    async def create_workflow(
        session: AsyncSession, workflow_data: WorkflowCreateRequest, user_id: int
    ) -> Workflow:
        """创建新工作流"""
        try:
            # 转换edges为字典列表格式 - TreeEdgeConfig是TypedDict，已经是字典
            edges_dict = []
            if hasattr(workflow_data.edges, '__iter__'):
                for edge in workflow_data.edges:
                    if isinstance(edge, dict):
                        # 已经是字典格式
                        edges_dict.append(edge)
                    elif hasattr(edge, 'dict'):
                        # Pydantic v1 style
                        edges_dict.append(edge.dict())
                    elif hasattr(edge, 'model_dump'):
                        # Pydantic v2 style
                        edges_dict.append(edge.model_dump())
                    else:
                        # 其他类型，尝试转换为字典
                        try:
                            edges_dict.append(dict(edge))
                        except:
                            edges_dict.append({})
            
            db_workflow = Workflow(
                name=workflow_data.name,
                description=workflow_data.description,
                version=workflow_data.version,
                type=workflow_data.type,
                nodes=workflow_data.nodes,
                edges=edges_dict,
                created_by=user_id,
                status=WorkflowStatus.ACTIVE,
            )

            session.add(db_workflow)
            await session.commit()
            await session.refresh(db_workflow)

            logger.info(
                f"Created workflow: {workflow_data.name} (ID: {db_workflow.id}) by user {user_id}"
            )
            return db_workflow

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create workflow: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建工作流失败",
            )

    @staticmethod
    async def get_workflow_by_id(
        session: AsyncSession, workflow_id: int, user_id: int
    ) -> Optional[Workflow]:
        """根据ID获取工作流"""
        statement = select(Workflow).where(
            (Workflow.id == workflow_id) & (Workflow.created_by == user_id)
        )
        # statement = select(Workflow).where(
        #     Workflow.id == workflow_id, Workflow.created_by == user_id
        # )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_workflows(
        session: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[WorkflowStatus] = None,
        search_term: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[List[Workflow], int]:
        """获取用户的工作流列表（分页+搜索+排序）"""

        # 构建基础查询条件
        conditions: List[Any] = [Workflow.created_by == user_id]

        # 添加状态过滤
        if status_filter:
            conditions.append(Workflow.status == status_filter)

        # 添加搜索条件
        if search_term:
            search_conditions: ColumnElement[bool] = or_(
                Workflow.name.ilike(f"%{search_term}%"),  # type: ignore
                Workflow.description.ilike(f"%{search_term}%"),  # type: ignore
            )
            conditions.append(search_conditions)

        # 构建排序 - 使用映射避免类型错误
        sort_mapping = {
            "created_at": Workflow.created_at,
            "updated_at": Workflow.updated_at,
            "name": Workflow.name,
            "status": Workflow.status,
        }
        sort_column = sort_mapping.get(sort_by, Workflow.created_at)
        if sort_order.lower() == "asc":
            order_clause = asc(sort_column)
        else:
            order_clause = desc(sort_column)

        # 构建查询
        statement = (
            select(Workflow)
            .where(*conditions)
            .offset(skip)
            .limit(limit)
            .order_by(order_clause)
        )

        result = await session.execute(statement)
        workflows = result.scalars().all()

        # 查询总数
        if conditions:
            count_statement = select(func.count()).select_from(Workflow).where(*conditions)
        else:
            count_statement = select(func.count()).select_from(Workflow)
        count_result = await session.execute(count_statement)
        total = count_result.scalar() or 0

        return list(workflows), total

    @staticmethod
    async def update_workflow(
        session: AsyncSession,
        workflow_id: int,
        workflow_data: WorkflowUpdateRequest,
        user_id: int,
    ) -> Optional[Workflow]:
        """更新工作流"""
        # 先获取工作流
        workflow = await WorkflowService.get_workflow_by_id(
            session, workflow_id, user_id
        )
        if not workflow:
            return None

        try:
            # 更新字段
            update_data = workflow_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(workflow, field):
                    setattr(workflow, field, value)

            # updated_at会自动更新（因为onupdate=func.now()）
            session.add(workflow)
            await session.commit()
            await session.refresh(workflow)

            logger.info(
                f"Updated workflow: {workflow.name} (ID: {workflow_id}) by user {user_id}"
            )
            return workflow

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to update workflow {workflow_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新工作流失败",
            )

    @staticmethod
    async def delete_workflow(
        session: AsyncSession, workflow_id: int, user_id: int
    ) -> bool:
        """删除工作流（软删除：设置为ARCHIVED状态）"""
        workflow = await WorkflowService.get_workflow_by_id(
            session, workflow_id, user_id
        )
        if not workflow:
            return False

        try:
            workflow.status = WorkflowStatus.ARCHIVED
            # updated_at会自动更新

            session.add(workflow)
            await session.commit()

            logger.info(
                f"Archived workflow: {workflow.name} (ID: {workflow_id}) by user {user_id}"
            )
            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to archive workflow {workflow_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除工作流失败",
            )

    @staticmethod
    async def check_workflow_access(
        session: AsyncSession, workflow_id: int, user_id: int
    ) -> bool:
        """检查用户是否有权限访问指定工作流"""
        statement = select(Workflow).where(
            (Workflow.id == workflow_id) &
            (Workflow.created_by == user_id) &
            (Workflow.status != WorkflowStatus.ARCHIVED)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none() is not None
