# API 使用指南

## 概述

本指南提供了ORE项目REST API的完整使用说明，包括认证、工作流管理、以及各种常见用例的代码示例。

## 基础信息

- **基础URL**: `http://localhost:8000`
- **API版本**: v1
- **认证方式**: JWT Bearer Token
- **内容类型**: `application/json`

## 快速开始

### 1. 启动服务

```bash
# 启动开发服务器
workflow-server

# 或使用uvicorn直接启动
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 访问API文档

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI规范**: <http://localhost:8000/openapi.json>

## 认证API

### 用户注册

注册新用户账户。

**端点**: `POST /api/v1/auth/register`

**请求体**:

```json
{
    "email": "user@example.com",
    "password": "secure_password123"
}
```

**响应**:

```json
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer"
    },
    "message": "注册成功",
    "timestamp": "2025-01-20T10:30:00Z"
}
```

**Python示例**:

```python
import requests

def register_user(email: str, password: str):
    url = "http://localhost:8000/api/v1/auth/register"
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        token = result["data"]["access_token"]
        print(f"注册成功，令牌: {token}")
        return token
    else:
        print(f"注册失败: {response.text}")
        return None

# 使用示例
token = register_user("test@example.com", "password123")
```

**JavaScript示例**:

```javascript
async function registerUser(email, password) {
    const response = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    });
    
    if (response.ok) {
        const result = await response.json();
        const token = result.data.access_token;
        console.log('注册成功，令牌:', token);
        return token;
    } else {
        console.error('注册失败:', await response.text());
        return null;
    }
}

// 使用示例
const token = await registerUser('test@example.com', 'password123');
```

### 用户登录

用现有账户登录。

**端点**: `POST /api/v1/auth/login`

**请求体**:

```json
{
    "email": "user@example.com",
    "password": "secure_password123"
}
```

**响应**:

```json
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer"
    },
    "message": "登录成功",
    "timestamp": "2025-01-20T10:30:00Z"
}
```

**Python示例**:

```python
def login_user(email: str, password: str):
    url = "http://localhost:8000/api/v1/auth/login"
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        token = result["data"]["access_token"]
        print(f"登录成功，令牌: {token}")
        return token
    else:
        print(f"登录失败: {response.text}")
        return None

# 使用示例
token = login_user("test@example.com", "password123")
```

### 使用认证令牌

获取令牌后，在后续请求中使用 `Authorization` 头：

```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get("http://localhost:8000/api/v1/protected-endpoint", headers=headers)
```

## 工作流API（扩展示例）

以下是工作流相关API的设计示例（实际实现可能有所不同）：

### 创建工作流

**端点**: `POST /api/v1/workflows`

**请求体**:

```json
{
    "workflow_name": "AI内容生成流程",
    "description": "自动化内容生成和审核",
    "config": {
        "workflow_id": "content-gen-001",
        "workflow_name": "AI内容生成流程",
        "description": "自动化内容生成和审核",
        "version": "1.0.0",
        "nodes": {
            "start": {
                "name": "开始",
                "node_type": "START",
                "description": "工作流入口"
            },
            "generate": {
                "name": "内容生成",
                "node_type": "PROCESS",
                "prompt": "生成关于指定主题的专业文章",
                "description": "AI内容生成"
            },
            "review": {
                "name": "内容审核",
                "node_type": "LEAF",
                "prompt": "审核内容质量和准确性",
                "description": "质量检查"
            }
        },
        "edges": [
            {
                "from_node": "start",
                "to_node": "generate",
                "input_config": {
                    "include_prompt": true,
                    "include_previous_output": true
                }
            },
            {
                "from_node": "generate",
                "to_node": "review",
                "input_config": {
                    "include_prompt": true,
                    "include_previous_output": true
                }
            }
        ]
    }
}
```

**Python示例**:

```python
def create_workflow(token: str, workflow_config: dict):
    url = "http://localhost:8000/api/v1/workflows"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=workflow_config, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        workflow_id = result["data"]["workflow_id"]
        print(f"工作流创建成功，ID: {workflow_id}")
        return workflow_id
    else:
        print(f"创建失败: {response.text}")
        return None

# 使用示例
workflow_config = {
    "workflow_name": "AI内容生成流程",
    "description": "自动化内容生成和审核",
    "config": {
        # ... 配置内容
    }
}

workflow_id = create_workflow(token, workflow_config)
```

### 执行工作流

**端点**: `POST /api/v1/workflows/{workflow_id}/execute`

**请求体**:

```json
{
    "input_data": {
        "topic": "人工智能的未来发展趋势",
        "target_audience": "技术专业人士",
        "word_count": 1000
    }
}
```

**Python示例**:

```python
def execute_workflow(token: str, workflow_id: str, input_data: dict):
    url = f"http://localhost:8000/api/v1/workflows/{workflow_id}/execute"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {"input_data": input_data}
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        execution_id = result["data"]["execution_id"]
        print(f"工作流执行已启动，执行ID: {execution_id}")
        return execution_id
    else:
        print(f"执行失败: {response.text}")
        return None

# 使用示例
input_data = {
    "topic": "人工智能的未来发展趋势",
    "target_audience": "技术专业人士",
    "word_count": 1000
}

execution_id = execute_workflow(token, workflow_id, input_data)
```

### 查询执行状态

**端点**: `GET /api/v1/workflows/executions/{execution_id}`

**响应**:

```json
{
    "success": true,
    "data": {
        "execution_id": "exec-123",
        "workflow_id": "content-gen-001",
        "status": "completed",
        "progress": {
            "total_nodes": 3,
            "completed_nodes": 3,
            "failed_nodes": 0
        },
        "results": {
            "start": "工作流启动完成",
            "generate": "# AI的未来发展趋势\n\n人工智能技术正在...",
            "review": "内容质量评分：95分，建议发布"
        },
        "started_at": "2025-01-20T10:30:00Z",
        "completed_at": "2025-01-20T10:35:00Z"
    }
}
```

**Python示例**:

```python
def get_execution_status(token: str, execution_id: str):
    url = f"http://localhost:8000/api/v1/workflows/executions/{execution_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        status = result["data"]["status"]
        print(f"执行状态: {status}")
        
        if status == "completed":
            results = result["data"]["results"]
            print("执行结果:")
            for node_id, output in results.items():
                print(f"  {node_id}: {output[:100]}...")
        
        return result["data"]
    else:
        print(f"查询失败: {response.text}")
        return None

# 使用示例 - 轮询执行状态
import time

while True:
    status_data = get_execution_status(token, execution_id)
    if status_data and status_data["status"] in ["completed", "failed"]:
        break
    time.sleep(5)  # 每5秒检查一次
```

## 系统API

### 健康检查

检查服务健康状态。

**端点**: `GET /health`

**响应**:

```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "timestamp": "2025-01-20T10:30:00Z",
        "version": "0.1.0"
    }
}
```

**Python示例**:

```python
def check_health():
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"服务状态: {result['data']['status']}")
            print(f"版本: {result['data']['version']}")
            return True
        else:
            print(f"健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"连接失败: {e}")
        return False

# 使用示例
if check_health():
    print("服务运行正常")
else:
    print("服务异常")
```

## 完整使用示例

### Python客户端封装

```python
import requests
import time
from typing import Optional, Dict, Any

class OREClient:
    """ORE API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def register(self, email: str, password: str) -> bool:
        """用户注册"""
        url = f"{self.base_url}/api/v1/auth/register"
        data = {"email": email, "password": password}
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            self.token = result["data"]["access_token"]
            return True
        return False
    
    def login(self, email: str, password: str) -> bool:
        """用户登录"""
        url = f"{self.base_url}/api/v1/auth/login"
        data = {"email": email, "password": password}
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            self.token = result["data"]["access_token"]
            return True
        return False
    
    def create_workflow(self, config: Dict[str, Any]) -> Optional[str]:
        """创建工作流"""
        url = f"{self.base_url}/api/v1/workflows"
        
        response = requests.post(url, json=config, headers=self._get_headers())
        if response.status_code == 200:
            result = response.json()
            return result["data"]["workflow_id"]
        return None
    
    def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Optional[str]:
        """执行工作流"""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/execute"
        data = {"input_data": input_data}
        
        response = requests.post(url, json=data, headers=self._get_headers())
        if response.status_code == 200:
            result = response.json()
            return result["data"]["execution_id"]
        return None
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """查询执行状态"""
        url = f"{self.base_url}/api/v1/workflows/executions/{execution_id}"
        
        response = requests.get(url, headers=self._get_headers())
        if response.status_code == 200:
            result = response.json()
            return result["data"]
        return None
    
    def wait_for_completion(self, execution_id: str, timeout: int = 300) -> Optional[Dict[str, Any]]:
        """等待执行完成"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status_data = self.get_execution_status(execution_id)
            if status_data and status_data["status"] in ["completed", "failed"]:
                return status_data
            time.sleep(5)
        
        return None  # 超时
    
    def health_check(self) -> bool:
        """健康检查"""
        url = f"{self.base_url}/health"
        
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

# 使用示例
def main():
    # 创建客户端
    client = OREClient()
    
    # 检查服务健康状态
    if not client.health_check():
        print("服务不可用")
        return
    
    # 注册/登录
    if not client.register("test@example.com", "password123"):
        if not client.login("test@example.com", "password123"):
            print("认证失败")
            return
    
    print("认证成功")
    
    # 创建工作流配置
    workflow_config = {
        "workflow_name": "AI内容生成流程",
        "description": "自动化内容生成",
        "config": {
            "workflow_id": "demo-workflow",
            "workflow_name": "演示工作流",
            "description": "演示用途",
            "version": "1.0.0",
            "nodes": {
                "start": {
                    "name": "开始",
                    "node_type": "START",
                    "description": "工作流入口"
                },
                "generate": {
                    "name": "内容生成",
                    "node_type": "LEAF",
                    "prompt": "生成一篇关于AI的文章",
                    "description": "AI内容生成"
                }
            },
            "edges": [
                {
                    "from_node": "start",
                    "to_node": "generate",
                    "input_config": {
                        "include_prompt": True,
                        "include_previous_output": True
                    }
                }
            ]
        }
    }
    
    # 创建工作流
    workflow_id = client.create_workflow(workflow_config)
    if not workflow_id:
        print("工作流创建失败")
        return
    
    print(f"工作流创建成功: {workflow_id}")
    
    # 执行工作流
    input_data = {
        "topic": "人工智能发展趋势",
        "length": "medium"
    }
    
    execution_id = client.execute_workflow(workflow_id, input_data)
    if not execution_id:
        print("工作流执行失败")
        return
    
    print(f"工作流执行已启动: {execution_id}")
    
    # 等待完成
    result = client.wait_for_completion(execution_id)
    if result:
        print(f"执行完成，状态: {result['status']}")
        if result['status'] == 'completed':
            print("执行结果:")
            for node_id, output in result['results'].items():
                print(f"  {node_id}: {output[:200]}...")
    else:
        print("执行超时或失败")

if __name__ == "__main__":
    main()
```

### JavaScript客户端示例

```javascript
class OREClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.token = null;
    }
    
    async register(email, password) {
        const response = await fetch(`${this.baseUrl}/api/v1/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        if (response.ok) {
            const result = await response.json();
            this.token = result.data.access_token;
            return true;
        }
        return false;
    }
    
    async login(email, password) {
        const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        if (response.ok) {
            const result = await response.json();
            this.token = result.data.access_token;
            return true;
        }
        return false;
    }
    
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }
    
    async createWorkflow(config) {
        const response = await fetch(`${this.baseUrl}/api/v1/workflows`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            const result = await response.json();
            return result.data.workflow_id;
        }
        return null;
    }
    
    async executeWorkflow(workflowId, inputData) {
        const response = await fetch(`${this.baseUrl}/api/v1/workflows/${workflowId}/execute`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ input_data: inputData })
        });
        
        if (response.ok) {
            const result = await response.json();
            return result.data.execution_id;
        }
        return null;
    }
    
    async getExecutionStatus(executionId) {
        const response = await fetch(`${this.baseUrl}/api/v1/workflows/executions/${executionId}`, {
            headers: this.getHeaders()
        });
        
        if (response.ok) {
            const result = await response.json();
            return result.data;
        }
        return null;
    }
    
    async waitForCompletion(executionId, timeout = 300000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const status = await this.getExecutionStatus(executionId);
            if (status && ['completed', 'failed'].includes(status.status)) {
                return status;
            }
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
        
        return null; // 超时
    }
    
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return response.ok;
        } catch {
            return false;
        }
    }
}

// 使用示例
async function main() {
    const client = new OREClient();
    
    // 健康检查
    if (!(await client.healthCheck())) {
        console.log('服务不可用');
        return;
    }
    
    // 登录
    if (!(await client.login('test@example.com', 'password123'))) {
        console.log('登录失败');
        return;
    }
    
    console.log('登录成功');
    
    // 创建并执行工作流
    const workflowConfig = {
        workflow_name: 'AI内容生成',
        description: '演示工作流',
        config: {
            // ... 工作流配置
        }
    };
    
    const workflowId = await client.createWorkflow(workflowConfig);
    if (!workflowId) {
        console.log('工作流创建失败');
        return;
    }
    
    const executionId = await client.executeWorkflow(workflowId, {
        topic: 'AI发展趋势'
    });
    
    if (!executionId) {
        console.log('工作流执行失败');
        return;
    }
    
    console.log(`工作流执行已启动: ${executionId}`);
    
    const result = await client.waitForCompletion(executionId);
    if (result) {
        console.log(`执行完成，状态: ${result.status}`);
        if (result.status === 'completed') {
            console.log('执行结果:', result.results);
        }
    }
}

// 运行示例
main().catch(console.error);
```

## 错误处理

### 常见错误码

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | 请求错误 | 请求参数不正确 |
| 401 | 未认证 | 需要有效的认证令牌 |
| 403 | 权限不足 | 没有访问权限 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 422 | 验证错误 | 请求数据验证失败 |
| 500 | 服务器错误 | 内部服务器错误 |

### 错误响应格式

```json
{
    "success": false,
    "error_code": "VALIDATION_ERROR",
    "message": "请求数据验证失败",
    "details": {
        "field": "email",
        "error": "邮箱格式不正确"
    },
    "timestamp": "2025-01-20T10:30:00Z"
}
```

### 错误处理示例

```python
def handle_api_response(response: requests.Response):
    """统一处理API响应"""
    if response.status_code == 200:
        return response.json()
    
    try:
        error_data = response.json()
        error_message = error_data.get('message', '未知错误')
        error_code = error_data.get('error_code', 'UNKNOWN_ERROR')
        
        print(f"API错误 [{error_code}]: {error_message}")
        
        if 'details' in error_data:
            print(f"详细信息: {error_data['details']}")
    
    except ValueError:
        print(f"HTTP错误 {response.status_code}: {response.text}")
    
    return None

# 使用示例
response = requests.post(url, json=data, headers=headers)
result = handle_api_response(response)
if result:
    # 处理成功响应
    pass
else:
    # 处理错误
    pass
```

## 最佳实践

### 1. 认证管理

- 安全存储访问令牌
- 实现令牌自动刷新机制
- 在令牌过期时自动重新认证

### 2. 错误处理

- 实现重试机制处理临时错误
- 使用指数退避算法避免频繁重试
- 记录详细的错误日志便于调试

### 3. 性能优化

- 使用连接池复用HTTP连接
- 实现请求缓存减少不必要的API调用
- 合理设置超时时间

### 4. 监控和日志

- 记录所有API调用的响应时间
- 监控错误率和成功率
- 实现健康检查和告警机制

这份API指南提供了完整的使用说明和代码示例，帮助开发者快速集成和使用ORE项目的API服务。