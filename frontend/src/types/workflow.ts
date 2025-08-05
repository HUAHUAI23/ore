/**
 * 工作流相关类型定义
 */

// 工作流状态枚举
export enum WorkflowStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  DELETED = 'deleted'
}

// 执行状态枚举
export enum ExecutionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

// 节点类型枚举
export enum NodeType {
  START = 'START',
  INTERMEDIATE = 'INTERMEDIATE', 
  LEAF = 'LEAF'
}

// 条件配置类型
export interface ConditionConfig {
  match_target: string // 匹配目标: "node_output"
  match_type: string // 匹配方式: "contains", "not_contains", "fuzzy", "regex"
  match_value: string // 匹配值
  case_sensitive: boolean // 是否区分大小写
}

// 输入配置类型
export interface TreeInputConfig {
  include_prompt: boolean
  include_previous_output: boolean
}

// 树形节点配置类型
export interface TreeNodeConfig {
  id: string
  name: string
  description: string
  prompt: string
  node_type: string // NodeType枚举值的字符串形式
  conditions?: ConditionConfig[] // 节点的输出条件配置
  input_config: TreeInputConfig // 节点的输入配置
  // 新增：节点在可视化编辑器中的位置信息
  position?: { x: number; y: number }
}

// 树形边配置类型
export interface TreeEdgeConfig {
  from_node: string // 源节点ID
  to_node: string // 目标节点ID
  condition?: ConditionConfig | null // 条件配置
}

// 工作流创建请求
export interface WorkflowCreateRequest {
  name: string
  description: string
  version: string
  type?: string
  nodes: Record<string, TreeNodeConfig>
  edges: TreeEdgeConfig[]
}

// 工作流更新请求
export interface WorkflowUpdateRequest {
  name?: string
  description?: string
  version?: string
  nodes?: Record<string, TreeNodeConfig>
  edges?: TreeEdgeConfig[]
  status?: WorkflowStatus
}

// 工作流响应
export interface WorkflowResponse {
  id: number
  name: string
  description: string
  version: string
  type: string
  nodes: Record<string, any>
  edges: any[]
  status: WorkflowStatus
  created_by: number
  created_at?: string
  updated_at?: string
}

// 工作流列表项
export interface WorkflowListItem {
  id: number
  name: string
  description: string
  version: string
  type: string
  status: WorkflowStatus
  created_at?: string
  updated_at?: string
}

// 工作流执行响应
export interface WorkflowExecutionResponse {
  id: number
  workflow_id: number
  status: ExecutionStatus
  result_data?: Record<string, any> | null
  error_message?: string | null
  total_nodes: number
  completed_nodes: number
  failed_nodes: number
  started_at?: string | null
  completed_at?: string | null
  created_at: string
}

// 工作流执行列表项
export interface WorkflowExecutionListItem {
  id: number
  workflow_id: number
  status: ExecutionStatus
  total_nodes: number
  completed_nodes: number
  failed_nodes: number
  started_at?: string | null
  completed_at?: string | null
  created_at: string
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

// 工作流执行统计
export interface WorkflowExecutionStats {
  execution_id: number
  success_rate: number
  duration_seconds?: number | null
  is_finished: boolean
}
