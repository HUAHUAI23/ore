"""
工作流执行服务层 - 修复数据库会话和类型问题
"""

import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, update
from sqlalchemy.orm import selectinload
from sqlmodel import select, func
from fastapi import HTTPException, status

from backend.models.workflow import WorkflowExecution, ExecutionStatus, Workflow
from backend.services.workflow import WorkflowService
from backend.utils.logger import get_logger
from workflow_engine.engines.tree.engine import TreeWorkflowEngine
from workflow_engine.engines.tree.types import ExecutionSummary

logger = get_logger(__name__)


class BackgroundTaskManager:
    """简化的后台任务管理器"""

    def __init__(self):
        self.running_tasks: Dict[int, asyncio.Task] = {}

    def start_task(self, execution_id: int, coroutine) -> None:
        """启动后台任务"""
        if execution_id in self.running_tasks:
            logger.warning(f"Task {execution_id} is already running")
            return

        task = asyncio.create_task(coroutine)
        self.running_tasks[execution_id] = task

        # 设置任务完成回调 - 自动清理
        task.add_done_callback(lambda t: self._cleanup_task(execution_id, t))

        logger.info(f"Started background task for execution {execution_id}")

    def _cleanup_task(self, execution_id: int, task: asyncio.Task) -> None:
        """任务完成时的清理"""
        if execution_id in self.running_tasks:
            del self.running_tasks[execution_id]

        if task.exception():
            logger.error(f"Task {execution_id} failed: {task.exception()}")
        else:
            logger.info(f"Task {execution_id} completed successfully")

    def is_running(self, execution_id: int) -> bool:
        """检查任务是否正在运行"""
        return execution_id in self.running_tasks

    def cancel_task(self, execution_id: int) -> bool:
        """取消任务"""
        if execution_id in self.running_tasks:
            task = self.running_tasks[execution_id]
            task.cancel()
            return True
        return False


# 全局任务管理器实例
task_manager = BackgroundTaskManager()


class DatabaseSessionManager:
    """数据库会话管理器 - 解决异步上下文管理器问题"""

    @staticmethod
    @asynccontextmanager
    async def get_session():
        """创建数据库会话的异步上下文管理器"""
        from backend.db import engine

        async with AsyncSession(engine) as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


class WorkflowExecutionService:
    """工作流执行服务类"""

    @staticmethod
    async def create_execution(
        session: AsyncSession, workflow_id: int, user_id: int
    ) -> WorkflowExecution:
        """创建工作流执行记录"""
        # 检查工作流是否存在和权限
        workflow = await WorkflowService.get_workflow_by_id(
            session, workflow_id, user_id
        )
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="工作流不存在或无权限访问"
            )

        try:
            # 计算总节点数
            total_nodes = len(workflow.nodes)

            db_execution = WorkflowExecution(
                workflow_id=workflow_id,
                status=ExecutionStatus.PENDING,
                total_nodes=total_nodes,
                completed_nodes=0,
                failed_nodes=0,
            )

            session.add(db_execution)
            await session.commit()
            await session.refresh(db_execution)

            logger.info(
                f"Created execution {db_execution.id} for workflow {workflow_id}"
            )
            return db_execution

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create execution: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建执行记录失败",
            )

    @staticmethod
    async def start_workflow_execution(
        session: AsyncSession, execution_id: int, user_id: int
    ) -> WorkflowExecution:
        """启动工作流执行（后台任务）"""
        execution = await WorkflowExecutionService.get_execution_by_id(
            session, execution_id, user_id
        )
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="执行记录不存在或无权限访问",
            )

        if execution.status != ExecutionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能执行状态为PENDING的工作流",
            )

        # 检查是否已有运行中的任务
        if task_manager.is_running(execution_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="工作流已在执行中"
            )

        # 获取工作流配置
        workflow = execution.workflow
        tree_config = workflow.to_tree_config()

        # 启动后台任务
        execution_coro = WorkflowExecutionService._execute_workflow_background(
            execution_id, tree_config
        )
        task_manager.start_task(execution_id, execution_coro)

        logger.info(f"Started workflow execution {execution_id} in background")
        return execution

    @staticmethod
    async def _execute_workflow_background(execution_id: int, tree_config) -> None:
        """后台执行工作流的核心逻辑"""

        try:
            # 1. 更新状态为运行中
            async with DatabaseSessionManager.get_session() as session:
                await WorkflowExecutionService._update_execution_status(
                    session,
                    execution_id,
                    ExecutionStatus.RUNNING,
                    started_at=datetime.now(timezone.utc),
                )

            # 2. 创建跟踪回调函数 - 每个回调都使用独立的会话
            async def on_execution_start(_workflow_id: str, execution_id: int) -> None:
                logger.info(f"Workflow execution {execution_id} started")

            async def on_node_completed(
                execution_id: int, node_id: str, result: Any
            ) -> None:
                try:
                    async with DatabaseSessionManager.get_session() as session:
                        await WorkflowExecutionService._update_node_result(
                            session, execution_id, node_id, result, is_success=True
                        )
                except Exception as e:
                    logger.error(f"Failed to update node completion: {e}")

            async def on_node_failed(
                execution_id: int, node_id: str, error: Exception
            ) -> None:
                try:
                    async with DatabaseSessionManager.get_session() as session:
                        await WorkflowExecutionService._update_node_result(
                            session, execution_id, node_id, str(error), is_success=False
                        )
                except Exception as e:
                    logger.error(f"Failed to update node failure: {e}")

            async def on_execution_finished(
                execution_id: int, summary: ExecutionSummary
            ) -> None:
                try:
                    async with DatabaseSessionManager.get_session() as session:
                        final_status = (
                            ExecutionStatus.COMPLETED
                            if summary.is_complete
                            else ExecutionStatus.FAILED
                        )
                        await WorkflowExecutionService._update_execution_status(
                            session,
                            execution_id,
                            final_status,
                            completed_at=datetime.now(timezone.utc),
                            result_data=summary.results,
                        )
                except Exception as e:
                    logger.error(f"Failed to update execution completion: {e}")

            # 3. 创建工作流引擎并执行
            tracking_callbacks = {
                "on_execution_start": on_execution_start,
                "on_node_completed": on_node_completed,
                "on_node_failed": on_node_failed,
                "on_execution_finished": on_execution_finished,
            }

            engine = TreeWorkflowEngine(tree_config, tracking_callbacks)
            engine.set_execution_id(execution_id)

            # 4. 执行工作流
            summary = await engine.execute_workflow()
            logger.info(
                f"Workflow execution {execution_id} completed with {summary.completed_count}/{summary.total_count} nodes"
            )

        except asyncio.CancelledError:
            # 处理任务取消
            logger.info(f"Workflow execution {execution_id} was cancelled")
            try:
                async with DatabaseSessionManager.get_session() as session:
                    await WorkflowExecutionService._update_execution_status(
                        session,
                        execution_id,
                        ExecutionStatus.CANCELLED,
                        completed_at=datetime.now(timezone.utc),
                    )
            except Exception as e:
                logger.error(f"Failed to update cancelled status: {e}")
            raise

        except Exception as e:
            logger.error(f"Workflow execution {execution_id} failed: {e}")

            # 更新执行状态为失败
            try:
                async with DatabaseSessionManager.get_session() as session:
                    await WorkflowExecutionService._update_execution_status(
                        session,
                        execution_id,
                        ExecutionStatus.FAILED,
                        completed_at=datetime.now(timezone.utc),
                        error_message=str(e),
                    )
            except Exception as db_error:
                logger.error(f"Failed to update failure status: {db_error}")

    @staticmethod
    async def _update_execution_status(
        session: AsyncSession,
        execution_id: int,
        status: ExecutionStatus,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """更新执行状态 - 修复类型问题"""
        try:
            # 构建更新字典 - 使用 Dict[str, Any] 避免类型错误
            update_values: Dict[str, Any] = {"status": status}

            if started_at is not None:
                update_values["started_at"] = started_at
            if completed_at is not None:
                update_values["completed_at"] = completed_at
            if result_data is not None:
                update_values["result_data"] = result_data
            if error_message is not None:
                update_values["error_message"] = error_message

            # 使用现代的update语句
            stmt = (
                update(WorkflowExecution)
                .where(WorkflowExecution.id == execution_id)  # type: ignore
                .values(**update_values)
            )

            await session.execute(stmt)
            await session.commit()

        except Exception as e:
            logger.error(f"Failed to update execution status: {e}")
            await session.rollback()
            raise

    @staticmethod
    async def _update_node_result(
        session: AsyncSession,
        execution_id: int,
        node_id: str,
        result: Any,
        is_success: bool = True,
    ) -> None:
        """更新节点执行结果"""
        try:
            # 先获取当前记录
            stmt = select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            db_result = await session.execute(stmt)
            execution = db_result.scalar_one_or_none()

            if not execution:
                logger.warning(f"Execution {execution_id} not found")
                return

            # 准备更新数据
            result_data = execution.result_data or {}
            result_data[node_id] = {
                "result": str(result),
                "success": is_success,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # 计算新的计数
            new_completed = execution.completed_nodes + (1 if is_success else 0)
            new_failed = execution.failed_nodes + (0 if is_success else 1)

            # 使用update语句更新
            update_stmt = (
                update(WorkflowExecution)
                .where(WorkflowExecution.id == execution_id)  # type: ignore
                .values(
                    result_data=result_data,
                    completed_nodes=new_completed,
                    failed_nodes=new_failed,
                )
            )

            await session.execute(update_stmt)
            await session.commit()

        except Exception as e:
            logger.error(f"Failed to update node result: {e}")
            await session.rollback()

    @staticmethod
    async def get_execution_by_id(
        session: AsyncSession, execution_id: int, user_id: int
    ) -> Optional[WorkflowExecution]:
        """根据ID获取执行记录"""
        stmt = (
            select(WorkflowExecution)
            .options(selectinload(WorkflowExecution.workflow))  # type: ignore
            .join(Workflow)
            .where(WorkflowExecution.id == execution_id, Workflow.created_by == user_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_workflow_executions(
        session: AsyncSession,
        workflow_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[WorkflowExecution], int]:
        """获取工作流的执行历史列表"""
        # 检查权限
        has_access = await WorkflowService.check_workflow_access(
            session, workflow_id, user_id
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="工作流不存在或无权限访问"
            )

        # 查询执行列表
        stmt = (
            select(WorkflowExecution)
            # 预加载 workflow 关联
            .options(selectinload(WorkflowExecution.workflow))  # type: ignore
            .where(WorkflowExecution.workflow_id == workflow_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(WorkflowExecution.created_at))  # type: ignore
        )

        result = await session.execute(stmt)
        executions = result.scalars().all()

        # 查询总数
        count_stmt = (
            select(func.count())
            .select_from(WorkflowExecution)
            .where(WorkflowExecution.workflow_id == workflow_id)
        )
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0

        return list(executions), total

    @staticmethod
    async def cancel_execution(
        session: AsyncSession, execution_id: int, user_id: int
    ) -> bool:
        """取消执行"""
        execution = await WorkflowExecutionService.get_execution_by_id(
            session, execution_id, user_id
        )
        if not execution:
            return False

        if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能取消PENDING或RUNNING状态的执行",
            )

        # 取消后台任务
        cancelled = task_manager.cancel_task(execution_id)

        # 更新数据库状态
        try:
            update_stmt = (
                update(WorkflowExecution)
                .where(WorkflowExecution.id == execution_id)  # type: ignore
                .values(
                    status=ExecutionStatus.CANCELLED,
                    completed_at=datetime.now(timezone.utc),
                )
            )

            await session.execute(update_stmt)
            await session.commit()

            logger.info(
                f"Cancelled execution {execution_id}, task_cancelled: {cancelled}"
            )
            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to cancel execution {execution_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="取消执行失败"
            )
