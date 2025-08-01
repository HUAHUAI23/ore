# 工作流核心API测试

## 概述

这个测试套件专注于测试4个关键的工作流API接口：

1. **工作流创建** - `POST /api/v1/workflows`
2. **工作流运行** - `POST /api/v1/workflows/{workflow_id}/run`
3. **工作流取消** - `POST /api/v1/workflows/executions/{execution_id}/cancel`
4. **执行详情查询** - `GET /api/v1/workflows/executions/{execution_id}`

## 测试数据

使用条件分支内容工作流作为测试数据，包含：
- 5个节点：start, content_classifier, technical_processor, marketing_processor, general_processor
- 4条边：支持条件分支逻辑
- 完整的TreeWorkflowConfig格式

## 运行测试

### 方式1: 运行所有核心测试
```bash
cd /path/to/ore
python -m pytest backend/tests/test_workflow_core_api.py -v
```

### 方式2: 运行单个测试
```bash
# 工作流创建测试
python -m pytest backend/tests/test_workflow_core_api.py::TestWorkflowCoreAPI::test_create_workflow_success -v

# 工作流运行测试
python -m pytest backend/tests/test_workflow_core_api.py::TestWorkflowCoreAPI::test_run_workflow_success -v

# 工作流取消测试
python -m pytest backend/tests/test_workflow_core_api.py::TestWorkflowCoreAPI::test_cancel_execution_success -v

# 执行详情查询测试
python -m pytest backend/tests/test_workflow_core_api.py::TestWorkflowCoreAPI::test_get_execution_detail_success -v

# 完整生命周期测试
python -m pytest backend/tests/test_workflow_core_api.py::TestWorkflowCoreAPI::test_complete_workflow_lifecycle -v
```

### 方式3: 使用便捷脚本
```bash
python backend/tests/run_core_tests.py
```

## 测试覆盖

### 正常流程测试
- ✅ 工作流创建成功
- ✅ 工作流运行成功
- ✅ 工作流取消成功
- ✅ 执行详情查询成功
- ✅ 完整生命周期测试

### 异常情况测试
- ✅ 未认证访问（403错误）
- ✅ 资源不存在（404错误）
- ✅ 无效数据（422错误）

### 数据验证
- ✅ 响应格式验证
- ✅ 字段完整性检查
- ✅ 状态转换验证（PENDING → RUNNING → COMPLETED/FAILED/CANCELLED）
- ✅ 节点数量验证
- ✅ 执行统计一致性检查（completed_nodes + failed_nodes ≤ total_nodes）

### 异步执行处理
- ✅ 状态轮询机制（`wait_for_execution_status_change`）
- ✅ 适当的等待时间控制
- ✅ 后台任务启动确认
- ✅ 取消操作的时序处理

## 测试依赖

测试使用以下fixture：
- `session` - 数据库会话（自动回滚）
- `client` - HTTP测试客户端
- `test_user` - 测试用户
- `auth_headers` - 认证头
- `conditional_workflow_data` - 条件分支工作流数据
- `created_workflow` - 已创建的工作流

## 注意事项

1. **数据库隔离**: 每个测试都在独立的事务中运行，测试结束后自动回滚
2. **后台执行特性**: 工作流执行是后台异步任务，测试充分考虑了这一特性：
   - 接口返回成功不代表执行完成，只是任务已启动
   - 包含状态轮询和等待机制
   - 考虑执行状态的异步转换（PENDING → RUNNING → COMPLETED/FAILED/CANCELLED）
3. **状态检查**: 测试会验证执行状态的正确转换和时序
4. **错误处理**: 涵盖了各种错误情况的测试
5. **时序控制**: 使用适当的等待时间确保后台任务有足够时间启动和状态转换

## 故障排除

如果测试失败，检查：
1. 数据库连接是否正常
2. 工作流引擎是否正确配置
3. 认证系统是否正常工作
4. API路由是否正确注册