"""
工作流核心API接口测试 - 专注于4个关键接口
考虑工作流执行是后台异步任务的特性
"""

import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User
from backend.models.workflow import ExecutionStatus


class TestWorkflowCoreAPI:
    """工作流核心API测试"""

    async def wait_for_execution_status_change(
        self,
        client: AsyncClient,
        auth_headers: dict,
        execution_id: int,
        initial_status: str = "PENDING",
        timeout: float = 5.0,
        check_interval: float = 0.2
    ) -> dict:
        """
        等待工作流执行状态改变（考虑到后台执行的异步特性）
        
        Args:
            client: HTTP客户端
            auth_headers: 认证头
            execution_id: 执行ID
            initial_status: 初始状态
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            执行详情数据
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # 获取当前执行状态
            response = await client.get(
                f"/api/v1/workflows/executions/{execution_id}",
                headers=auth_headers
            )
            
            if response.status_code == 200:
                data = response.json()["data"]
                current_status = data["status"]
                
                # 如果状态已改变，返回数据
                if current_status != initial_status:
                    return data
                
                # 检查是否超时
                if asyncio.get_event_loop().time() - start_time > timeout:
                    # 超时也返回当前数据，让调用者决定如何处理
                    return data
                
                # 等待一段时间再检查
                await asyncio.sleep(check_interval)
            else:
                # 如果请求失败，返回空数据
                return {}

    @pytest_asyncio.fixture
    async def conditional_workflow_data(self) -> dict:
        """条件分支内容工作流测试数据"""
        return {
            "name": "条件分支内容工作流",
            "description": "根据内容类型选择不同处理路径",
            "version": "1.0.0",
            "type": "tree",
            "nodes": {
                "start": {
                    "id": "start",
                    "name": "启动",
                    "description": "工作流开始",
                    "prompt": "",
                    "node_type": "START",
                    "input_config": {
                        "include_prompt": True,
                        "include_previous_output": True,
                    },
                },
                "content_classifier": {
                    "id": "content_classifier",
                    "name": "内容分类器",
                    "description": "分析内容类型并输出分类结果",
                    "prompt": '请分析输入内容的类型，并明确输出分类结果。可能的类型：技术文章、营销文案、新闻报道、学术论文。请在回答开头明确说明："内容类型：[具体类型]"',
                    "node_type": "INTERMEDIATE",
                    "input_config": {
                        "include_prompt": True,
                        "include_previous_output": True,
                    },
                },
                "technical_processor": {
                    "id": "technical_processor",
                    "name": "技术文章处理器",
                    "description": "专门处理技术类内容",
                    "prompt": "作为技术专家，请对以下技术内容进行深度分析和优化，包括技术准确性检查、代码示例优化、最佳实践建议等。",
                    "node_type": "LEAF",
                    "input_config": {
                        "include_prompt": True,
                        "include_previous_output": True,
                    },
                },
                "marketing_processor": {
                    "id": "marketing_processor",
                    "name": "营销文案处理器",
                    "description": "专门处理营销类内容",
                    "prompt": "作为营销专家，请对以下营销内容进行优化，包括吸引力提升、转化率优化、受众定位分析等。",
                    "node_type": "LEAF",
                    "input_config": {
                        "include_prompt": True,
                        "include_previous_output": True,
                    },
                },
                "general_processor": {
                    "id": "general_processor",
                    "name": "通用处理器",
                    "description": "处理其他类型内容",
                    "prompt": "请对以下内容进行通用优化，包括结构调整、语言润色、逻辑完善等。",
                    "node_type": "LEAF",
                    "input_config": {
                        "include_prompt": True,
                        "include_previous_output": True,
                    },
                },
            },
            "edges": [
                {
                    "from_node": "start",
                    "to_node": "content_classifier",
                    "condition": None,
                },
                {
                    "from_node": "content_classifier",
                    "to_node": "technical_processor",
                    "condition": {
                        "match_target": "node_output",
                        "match_type": "contains",
                        "match_value": "技术文章",
                        "case_sensitive": False,
                    },
                },
                {
                    "from_node": "content_classifier",
                    "to_node": "marketing_processor",
                    "condition": {
                        "match_target": "node_output",
                        "match_type": "contains",
                        "match_value": "营销文案",
                        "case_sensitive": False,
                    },
                },
                {
                    "from_node": "content_classifier",
                    "to_node": "general_processor",
                    "condition": {
                        "match_target": "node_output",
                        "match_type": "not_contains",
                        "match_value": "技术文章",
                        "case_sensitive": False,
                    },
                },
            ],
        }

    @pytest_asyncio.fixture
    async def created_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        conditional_workflow_data: dict
    ):
        """创建测试工作流并返回工作流数据"""
        response = await client.post(
            "/api/v1/workflows",
            json=conditional_workflow_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        return response.json()["data"]

    # ============================================
    # 0. 测试工具方法
    # ============================================

    @pytest.mark.asyncio
    async def test_print_test_user_token(
        self,
        test_user: User,
        auth_headers: dict
    ):
        """打印测试用户的token - 用于开发和调试"""
        from backend.services.auth import AuthService
        
        # 生成token
        token = AuthService.create_user_token(test_user)
        
        # 打印用户信息和token
        print(f"\n{'='*60}")
        print(f"测试用户信息:")
        print(f"  ID: {test_user.id}")
        print(f"  用户名: {test_user.name}")
        print(f"  昵称: {test_user.nickname}")
        print(f"  邮箱: {test_user.email}")
        print(f"  是否激活: {test_user.is_active}")
        print(f"{'='*60}")
        print(f"Bearer Token:")
        print(f"  {token}")
        print(f"{'='*60}")
        print(f"Authorization Header:")
        print(f"  Authorization: Bearer {token}")
        print(f"{'='*60}")
        print(f"curl 示例:")
        print(f'  curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/workflows')
        print(f"{'='*60}\n")
        
        # 验证token有效性
        assert token is not None
        assert len(token) > 0
        assert token.startswith("eyJ")  # JWT token应该以eyJ开头
        
        # 验证auth_headers格式
        assert "Authorization" in auth_headers
        assert auth_headers["Authorization"].startswith("Bearer ")
        
        # 测试通过，主要目的是打印token
        assert True

    # ============================================
    # 1. 工作流创建接口测试
    # ============================================

    @pytest.mark.asyncio
    async def test_create_workflow_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        conditional_workflow_data: dict
    ):
        """测试成功创建条件分支工作流"""
        response = await client.post(
            "/api/v1/workflows",
            json=conditional_workflow_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["message"] == "工作流创建成功"
        assert "data" in data
        
        workflow_data = data["data"]
        assert workflow_data["name"] == "条件分支内容工作流"
        assert workflow_data["description"] == "根据内容类型选择不同处理路径"
        assert workflow_data["version"] == "1.0.0"
        assert workflow_data["type"] == "tree"
        assert "id" in workflow_data
        assert "created_at" in workflow_data
        
        # 验证节点和边数据
        assert len(workflow_data["nodes"]) == 5
        assert len(workflow_data["edges"]) == 4
        assert "start" in workflow_data["nodes"]
        assert "content_classifier" in workflow_data["nodes"]

    @pytest.mark.asyncio
    async def test_create_workflow_unauthorized(
        self,
        client: AsyncClient,
        conditional_workflow_data: dict
    ):
        """测试未认证用户创建工作流"""
        response = await client.post(
            "/api/v1/workflows",
            json=conditional_workflow_data
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_workflow_invalid_data(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """测试无效数据创建工作流"""
        invalid_data = {
            "name": "",  # 空名称
            "description": "test",
            "version": "1.0.0",
            "nodes": {},  # 空节点
            "edges": []
        }
        
        response = await client.post(
            "/api/v1/workflows",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    # ============================================
    # 2. 工作流运行接口测试
    # ============================================

    @pytest.mark.asyncio
    async def test_run_workflow_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        created_workflow: dict
    ):
        """测试成功运行条件分支工作流（考虑后台执行特性）"""
        workflow_id = created_workflow["id"]
        
        # 1. 启动工作流执行
        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/run",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["message"] == "工作流已开始运行"
        assert "data" in data
        
        execution_data = data["data"]
        assert execution_data["workflow_id"] == workflow_id
        assert "id" in execution_data
        assert execution_data["status"] == "PENDING"  # 初始状态应该是PENDING
        assert "created_at" in execution_data
        assert execution_data["total_nodes"] == 5  # 5个节点
        
        execution_id = execution_data["id"]
        
        # 2. 等待执行状态改变（从PENDING到RUNNING或其他状态）
        updated_execution = await self.wait_for_execution_status_change(
            client, auth_headers, execution_id, "PENDING", timeout=3.0
        )
        
        # 3. 验证状态已经改变
        if updated_execution:
            assert updated_execution["status"] in ["RUNNING", "COMPLETED", "FAILED"]
            # 如果是RUNNING状态，说明后台任务已经开始
            # 如果是COMPLETED/FAILED，说明执行很快就完成了

    @pytest.mark.asyncio
    async def test_run_workflow_unauthorized(
        self,
        client: AsyncClient,
        created_workflow: dict
    ):
        """测试未认证用户运行工作流"""
        workflow_id = created_workflow["id"]
        
        response = await client.post(f"/api/v1/workflows/{workflow_id}/run")
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_run_nonexistent_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """测试运行不存在的工作流"""
        response = await client.post(
            "/api/v1/workflows/99999/run",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    # ============================================
    # 3. 工作流取消接口测试
    # ============================================

    @pytest.mark.asyncio
    async def test_cancel_execution_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        created_workflow: dict
    ):
        """测试成功取消工作流执行（考虑后台执行特性）"""
        workflow_id = created_workflow["id"]
        
        # 1. 启动工作流执行
        run_response = await client.post(
            f"/api/v1/workflows/{workflow_id}/run",
            headers=auth_headers
        )
        assert run_response.status_code == 200
        execution_id = run_response.json()["data"]["id"]
        
        # 2. 等待执行开始（从PENDING变为RUNNING）
        # 或者至少给后台任务一些时间来启动
        await asyncio.sleep(0.5)  # 增加等待时间确保后台任务启动
        
        # 3. 尝试取消执行
        cancel_response = await client.post(
            f"/api/v1/workflows/executions/{execution_id}/cancel",
            headers=auth_headers
        )
        
        # 4. 验证取消请求成功
        assert cancel_response.status_code == 200
        data = cancel_response.json()
        assert data["success"] is True
        assert data["message"] == "工作流执行已取消"
        
        # 5. 等待状态更新为CANCELLED
        await asyncio.sleep(0.3)
        
        # 6. 验证最终状态
        final_response = await client.get(
            f"/api/v1/workflows/executions/{execution_id}",
            headers=auth_headers
        )
        assert final_response.status_code == 200
        final_data = final_response.json()["data"]
        
        # 状态应该是CANCELLED，或者如果执行很快完成了，可能是COMPLETED/FAILED
        assert final_data["status"] in ["CANCELLED", "COMPLETED", "FAILED"]

    @pytest.mark.asyncio
    async def test_cancel_execution_unauthorized(
        self,
        client: AsyncClient,
        created_workflow: dict,
        auth_headers: dict
    ):
        """测试未认证用户取消工作流执行"""
        workflow_id = created_workflow["id"]
        
        # 先启动一个执行
        run_response = await client.post(
            f"/api/v1/workflows/{workflow_id}/run",
            headers=auth_headers
        )
        assert run_response.status_code == 200
        execution_id = run_response.json()["data"]["id"]
        
        # 给后台任务一些启动时间
        await asyncio.sleep(0.2)
        
        # 尝试未认证取消执行
        cancel_response = await client.post(
            f"/api/v1/workflows/executions/{execution_id}/cancel"
        )
        
        assert cancel_response.status_code == 403

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_execution(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """测试取消不存在的执行"""
        response = await client.post(
            "/api/v1/workflows/executions/99999/cancel",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    # ============================================
    # 4. 执行详情查询接口测试
    # ============================================

    @pytest.mark.asyncio
    async def test_get_execution_detail_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        created_workflow: dict
    ):
        """测试成功获取工作流执行详情（考虑后台执行特性）"""
        workflow_id = created_workflow["id"]
        
        # 1. 启动工作流执行
        run_response = await client.post(
            f"/api/v1/workflows/{workflow_id}/run",
            headers=auth_headers
        )
        assert run_response.status_code == 200
        execution_id = run_response.json()["data"]["id"]
        
        # 2. 立即获取执行详情（此时可能还是PENDING状态）
        detail_response = await client.get(
            f"/api/v1/workflows/executions/{execution_id}",
            headers=auth_headers
        )
        
        assert detail_response.status_code == 200
        data = detail_response.json()
        
        assert data["success"] is True
        assert "data" in data
        
        execution_data = data["data"]
        assert execution_data["id"] == execution_id
        assert execution_data["workflow_id"] == workflow_id
        assert execution_data["status"] in ["PENDING", "RUNNING", "COMPLETED", "FAILED"]
        assert "created_at" in execution_data
        assert execution_data["total_nodes"] == 5
        assert execution_data["completed_nodes"] >= 0
        assert execution_data["failed_nodes"] >= 0
        
        # 3. 等待一段时间后再次检查（看看状态是否有变化）
        await asyncio.sleep(0.5)
        
        updated_response = await client.get(
            f"/api/v1/workflows/executions/{execution_id}",
            headers=auth_headers
        )
        assert updated_response.status_code == 200
        updated_data = updated_response.json()["data"]
        
        # 验证状态可能已经改变
        assert updated_data["status"] in ["PENDING", "RUNNING", "COMPLETED", "FAILED"]
        
        # 如果状态是RUNNING或COMPLETED，说明后台任务已经开始或完成
        if updated_data["status"] in ["RUNNING", "COMPLETED"]:
            # 可能会有一些节点已经完成
            assert updated_data["completed_nodes"] >= 0

    @pytest.mark.asyncio
    async def test_get_execution_detail_unauthorized(
        self,
        client: AsyncClient,
        created_workflow: dict,
        auth_headers: dict
    ):
        """测试未认证用户获取工作流执行详情"""
        workflow_id = created_workflow["id"]
        
        # 先启动一个执行
        run_response = await client.post(
            f"/api/v1/workflows/{workflow_id}/run",
            headers=auth_headers
        )
        assert run_response.status_code == 200
        execution_id = run_response.json()["data"]["id"]
        
        # 尝试未认证获取执行详情
        detail_response = await client.get(
            f"/api/v1/workflows/executions/{execution_id}"
        )
        
        assert detail_response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_nonexistent_execution_detail(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """测试获取不存在的执行详情"""
        response = await client.get(
            "/api/v1/workflows/executions/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    # ============================================
    # 5. 综合流程测试
    # ============================================

    @pytest.mark.asyncio
    async def test_complete_workflow_lifecycle(
        self,
        client: AsyncClient,
        auth_headers: dict,
        conditional_workflow_data: dict
    ):
        """测试完整的工作流生命周期：创建 -> 运行 -> 查询 -> 取消（考虑后台执行特性）"""
        
        # 1. 创建工作流
        create_response = await client.post(
            "/api/v1/workflows",
            json=conditional_workflow_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        workflow_id = create_response.json()["data"]["id"]
        
        # 2. 运行工作流
        run_response = await client.post(
            f"/api/v1/workflows/{workflow_id}/run",
            headers=auth_headers
        )
        assert run_response.status_code == 200
        execution_data = run_response.json()["data"]
        execution_id = execution_data["id"]
        
        # 验证初始状态
        assert execution_data["status"] == "PENDING"
        
        # 3. 立即查询执行详情
        detail_response = await client.get(
            f"/api/v1/workflows/executions/{execution_id}",
            headers=auth_headers
        )
        assert detail_response.status_code == 200
        execution_detail = detail_response.json()["data"]
        assert execution_detail["workflow_id"] == workflow_id
        assert execution_detail["status"] in ["PENDING", "RUNNING"]
        
        # 4. 等待后台任务启动
        await asyncio.sleep(0.5)
        
        # 5. 尝试取消执行
        cancel_response = await client.post(
            f"/api/v1/workflows/executions/{execution_id}/cancel",
            headers=auth_headers
        )
        assert cancel_response.status_code == 200
        
        # 6. 等待状态更新
        await asyncio.sleep(0.5)
        
        # 7. 最终状态检查
        final_detail_response = await client.get(
            f"/api/v1/workflows/executions/{execution_id}",
            headers=auth_headers
        )
        assert final_detail_response.status_code == 200
        final_execution = final_detail_response.json()["data"]
        
        # 状态应该是已取消、已完成或失败
        # 注意：如果工作流执行很快，可能在取消之前就完成了
        assert final_execution["status"] in ["CANCELLED", "COMPLETED", "FAILED"]
        
        # 8. 验证执行统计数据的一致性
        total_nodes = final_execution["total_nodes"]
        completed_nodes = final_execution["completed_nodes"]
        failed_nodes = final_execution["failed_nodes"]
        
        assert total_nodes == 5  # 应该有5个节点
        assert completed_nodes >= 0
        assert failed_nodes >= 0
        assert completed_nodes + failed_nodes <= total_nodes  # 逻辑一致性检查