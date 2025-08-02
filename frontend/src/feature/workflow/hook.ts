/**
 * 工作流相关的React hooks
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

import * as workflowApi from '@/api/workflow'
import type {
  WorkflowCreateRequest,
  WorkflowUpdateRequest,
  WorkflowStatus
} from '@/types/workflow'

// ======================
// 查询相关hooks
// ======================

/**
 * 获取工作流列表
 */
export const useWorkflows = (params?: {
  skip?: number
  limit?: number
  status_filter?: WorkflowStatus
}) => {
  return useQuery({
    queryKey: ['workflows', params],
    queryFn: () => workflowApi.getWorkflows(params),
    staleTime: 5 * 60 * 1000, // 5分钟
  })
}

/**
 * 获取工作流详情
 */
export const useWorkflow = (workflowId: number, enabled = true) => {
  return useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: () => workflowApi.getWorkflow(workflowId),
    enabled: enabled && workflowId > 0,
    staleTime: 2 * 60 * 1000, // 2分钟
  })
}

/**
 * 获取工作流执行历史
 */
export const useWorkflowExecutions = (
  workflowId: number,
  params?: {
    skip?: number
    limit?: number
  },
  enabled = true
) => {
  return useQuery({
    queryKey: ['workflow-executions', workflowId, params],
    queryFn: () => workflowApi.getWorkflowExecutions(workflowId, params),
    enabled: enabled && workflowId > 0,
    refetchInterval: 5000, // 每5秒刷新一次
    staleTime: 0, // 立即过期，确保数据实时性
  })
}

/**
 * 获取执行详情
 */
export const useExecutionDetail = (executionId: number, enabled = true) => {
  return useQuery({
    queryKey: ['execution-detail', executionId],
    queryFn: () => workflowApi.getExecutionDetail(executionId),
    enabled: enabled && executionId > 0,
    staleTime: 30 * 1000, // 30秒
  })
}

// ======================
// 变更相关hooks
// ======================

/**
 * 创建工作流
 */
export const useCreateWorkflow = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: WorkflowCreateRequest) => workflowApi.createWorkflow(data),
    onSuccess: (data) => {
      toast.success('工作流创建成功')
      // 使相关查询失效
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
    },
    onError: (error: any) => {
      toast.error(error?.message || '创建工作流失败')
    },
  })
}

/**
 * 更新工作流
 */
export const useUpdateWorkflow = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ workflowId, data }: { workflowId: number; data: WorkflowUpdateRequest }) =>
      workflowApi.updateWorkflow(workflowId, data),
    onSuccess: (data, variables) => {
      toast.success('工作流更新成功')
      // 使相关查询失效
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
      queryClient.invalidateQueries({ queryKey: ['workflow', variables.workflowId] })
    },
    onError: (error: any) => {
      toast.error(error?.message || '更新工作流失败')
    },
  })
}

/**
 * 删除工作流
 */
export const useDeleteWorkflow = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (workflowId: number) => workflowApi.deleteWorkflow(workflowId),
    onSuccess: () => {
      toast.success('工作流删除成功')
      // 使相关查询失效
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
    },
    onError: (error: any) => {
      toast.error(error?.message || '删除工作流失败')
    },
  })
}

/**
 * 运行工作流
 */
export const useRunWorkflow = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (workflowId: number) => workflowApi.runWorkflow(workflowId),
    onSuccess: (data, workflowId) => {
      toast.success('工作流开始运行')
      // 刷新执行历史
      queryClient.invalidateQueries({ queryKey: ['workflow-executions', workflowId] })
    },
    onError: (error: any) => {
      toast.error(error?.message || '运行工作流失败')
    },
  })
}

/**
 * 取消工作流执行
 */
export const useCancelExecution = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (executionId: number) => workflowApi.cancelExecution(executionId),
    onSuccess: () => {
      toast.success('工作流执行已取消')
      // 刷新相关查询
      queryClient.invalidateQueries({ queryKey: ['workflow-executions'] })
      queryClient.invalidateQueries({ queryKey: ['execution-detail'] })
    },
    onError: (error: any) => {
      toast.error(error?.message || '取消执行失败')
    },
  })
}