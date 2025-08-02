import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { toast } from 'sonner'

import * as workflowApi from '@/api/workflow'
import type {
  WorkflowCreateRequest,
  WorkflowStatus,
  WorkflowUpdateRequest,
} from '@/types/workflow'

// Query keys
export const workflowKeys = {
  all: ['workflows'] as const,
  lists: () => [...workflowKeys.all, 'list'] as const,
  list: (filters: Record<string, unknown>) => [...workflowKeys.lists(), filters] as const,
  details: () => [...workflowKeys.all, 'detail'] as const,
  detail: (id: number) => [...workflowKeys.details(), id] as const,
  executions: (workflowId: number) => [...workflowKeys.all, 'executions', workflowId] as const,
  execution: (executionId: number) => [...workflowKeys.all, 'execution', executionId] as const,
}

// ======================
// 工作流CRUD相关hooks
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
    queryKey: workflowKeys.list(params || {}),
    queryFn: () => workflowApi.getWorkflows(params),
    staleTime: 1 * 60 * 1000, // 1分钟
  })
}

/**
 * 获取工作流详情
 */
export const useWorkflow = (workflowId: number) => {
  return useQuery({
    queryKey: workflowKeys.detail(workflowId),
    queryFn: () => workflowApi.getWorkflow(workflowId),
    enabled: !!workflowId,
    staleTime: 5 * 60 * 1000, // 5分钟
  })
}

/**
 * 创建工作流
 */
export const useCreateWorkflow = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: WorkflowCreateRequest) => workflowApi.createWorkflow(data),
    onSuccess: (response) => {
      // 更新工作流列表缓存
      queryClient.invalidateQueries({ queryKey: workflowKeys.lists() })
      
      toast.success('工作流创建成功')
      
      // 跳转到工作流编辑页面
      navigate({ to: `/workflows/${response.id}` })
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : '创建工作流失败'
      toast.error(message)
    },
  })
}

/**
 * 更新工作流
 */
export const useUpdateWorkflow = (workflowId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: WorkflowUpdateRequest) => workflowApi.updateWorkflow(workflowId, data),
    onSuccess: (response) => {
      // 更新相关缓存
      queryClient.setQueryData(workflowKeys.detail(workflowId), response)
      queryClient.invalidateQueries({ queryKey: workflowKeys.lists() })
      
      toast.success('工作流更新成功')
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : '更新工作流失败'
      toast.error(message)
    },
  })
}

/**
 * 删除工作流
 */
export const useDeleteWorkflow = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (workflowId: number) => workflowApi.deleteWorkflow(workflowId),
    onSuccess: (_, workflowId) => {
      // 更新缓存
      queryClient.invalidateQueries({ queryKey: workflowKeys.lists() })
      queryClient.removeQueries({ queryKey: workflowKeys.detail(workflowId) })
      
      toast.success('工作流删除成功')
      
      // 跳转到工作流列表页面
      navigate({ to: '/' })
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : '删除工作流失败'
      toast.error(message)
    },
  })
}

// ======================
// 工作流执行相关hooks
// ======================

/**
 * 运行工作流
 */
export const useRunWorkflow = (workflowId?: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id?: number) => {
      const targetId = id || workflowId
      if (!targetId) throw new Error('工作流ID不能为空')
      return workflowApi.runWorkflow(targetId)
    },
    onSuccess: (_, id) => {
      const targetId = id || workflowId
      if (targetId) {
        // 更新执行历史缓存
        queryClient.invalidateQueries({ queryKey: workflowKeys.executions(targetId) })
      }
      
      toast.success('工作流开始执行')
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : '执行工作流失败'
      toast.error(message)
    },
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
  }
) => {
  return useQuery({
    queryKey: workflowKeys.executions(workflowId),
    queryFn: () => workflowApi.getWorkflowExecutions(workflowId, params),
    enabled: !!workflowId,
    refetchInterval: 5000, // 每5秒刷新一次执行状态
    staleTime: 1000, // 1秒后数据过期，确保及时更新执行状态
  })
}

/**
 * 获取执行详情
 */
export const useExecutionDetail = (executionId: number) => {
  return useQuery({
    queryKey: workflowKeys.execution(executionId),
    queryFn: () => workflowApi.getExecutionDetail(executionId),
    enabled: !!executionId,
    staleTime: 30 * 1000, // 30秒
  })
}

/**
 * 取消执行
 */
export const useCancelExecution = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (executionId: number) => workflowApi.cancelExecution(executionId),
    onSuccess: (_, executionId) => {
      // 更新执行详情缓存
      queryClient.invalidateQueries({ queryKey: workflowKeys.execution(executionId) })
      
      toast.success('执行已取消')
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : '取消执行失败'
      toast.error(message)
    },
  })
}
