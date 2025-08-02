/**
 * 工作流相关API接口
 */

import { get, post, put, del } from '@/api'
import type {
  WorkflowCreateRequest,
  WorkflowUpdateRequest,
  WorkflowResponse,
  WorkflowListItem,
  WorkflowExecutionResponse,
  WorkflowExecutionListItem,
  PaginatedResponse,
  WorkflowStatus
} from '@/types/workflow'

// ======================
// 工作流CRUD接口
// ======================

/**
 * 创建工作流
 */
export const createWorkflow = (data: WorkflowCreateRequest): Promise<WorkflowResponse> => {
  return post<WorkflowResponse>('/workflows', data)
}

/**
 * 获取工作流列表
 */
export const getWorkflows = (params?: {
  skip?: number
  limit?: number
  status_filter?: WorkflowStatus
}): Promise<PaginatedResponse<WorkflowListItem>> => {
  const searchParams = new URLSearchParams()
  
  if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString())
  if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString())
  if (params?.status_filter) searchParams.append('status_filter', params.status_filter)
  
  const queryString = searchParams.toString()
  const url = queryString ? `/workflows?${queryString}` : '/workflows'
  
  return get<PaginatedResponse<WorkflowListItem>>(url)
}

/**
 * 获取工作流详情
 */
export const getWorkflow = (workflowId: number): Promise<WorkflowResponse> => {
  return get<WorkflowResponse>(`/workflows/${workflowId}`)
}

/**
 * 更新工作流
 */
export const updateWorkflow = (
  workflowId: number, 
  data: WorkflowUpdateRequest
): Promise<WorkflowResponse> => {
  return put<WorkflowResponse>(`/workflows/${workflowId}`, data)
}

/**
 * 删除工作流（软删除）
 */
export const deleteWorkflow = (workflowId: number): Promise<void> => {
  return del<void>(`/workflows/${workflowId}`)
}

// ======================
// 工作流执行相关接口
// ======================

/**
 * 运行工作流
 */
export const runWorkflow = (workflowId: number): Promise<WorkflowExecutionResponse> => {
  return post<WorkflowExecutionResponse>(`/workflows/${workflowId}/run`)
}

/**
 * 获取工作流执行历史列表
 */
export const getWorkflowExecutions = (
  workflowId: number,
  params?: {
    skip?: number
    limit?: number
  }
): Promise<PaginatedResponse<WorkflowExecutionListItem>> => {
  const searchParams = new URLSearchParams()
  
  if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString())
  if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString())
  
  const queryString = searchParams.toString()
  const url = queryString 
    ? `/workflows/${workflowId}/executions?${queryString}`
    : `/workflows/${workflowId}/executions`
  
  return get<PaginatedResponse<WorkflowExecutionListItem>>(url)
}

/**
 * 获取工作流执行详情
 */
export const getExecutionDetail = (executionId: number): Promise<WorkflowExecutionResponse> => {
  return get<WorkflowExecutionResponse>(`/workflows/executions/${executionId}`)
}

/**
 * 取消工作流执行
 */
export const cancelExecution = (executionId: number): Promise<void> => {
  return post<void>(`/workflows/executions/${executionId}/cancel`)
}
