/**
 * 工作流相关的Zod验证模式
 */

import { z } from 'zod'

import { NodeType, WorkflowStatus } from '@/types/workflow'

// 条件配置验证
export const conditionConfigSchema = z.object({
  match_target: z.string().default('node_output'),
  match_type: z.enum(['contains', 'not_contains', 'fuzzy', 'regex']),
  match_value: z.string().min(1, '匹配值不能为空'),
  case_sensitive: z.boolean().default(true)
})

// 输入配置验证
export const treeInputConfigSchema = z.object({
  include_prompt: z.boolean().default(true),
  include_previous_output: z.boolean().default(true)
})

// 节点配置验证
export const treeNodeConfigSchema = z.object({
  id: z.string().min(1, '节点ID不能为空'),
  name: z.string().min(1, '节点名称不能为空').max(200, '节点名称不能超过200字符'),
  description: z.string().max(1000, '节点描述不能超过1000字符'),
  prompt: z.string(),
  node_type: z.nativeEnum(NodeType),
  conditions: z.array(conditionConfigSchema).optional(),
  input_config: treeInputConfigSchema, // 节点级别的输入配置
  // 新增：位置信息验证
  position: z.object({
    x: z.number(),
    y: z.number()
  }).optional()
})

// 边配置验证
export const treeEdgeConfigSchema = z.object({
  from_node: z.string().min(1, '源节点ID不能为空'),
  to_node: z.string().min(1, '目标节点ID不能为空'),
  condition: conditionConfigSchema.optional().nullable()
})

// 工作流创建验证
export const workflowCreateSchema = z.object({
  name: z.string().min(1, '工作流名称不能为空').max(200, '工作流名称不能超过200字符'),
  description: z.string().max(1000, '工作流描述不能超过1000字符'),
  version: z.string().min(1, '版本号不能为空').max(50, '版本号不能超过50字符'),
  type: z.string().default('tree'),
  nodes: z.record(z.string(), treeNodeConfigSchema).refine(
    (nodes) => {
      const startNodes = Object.values(nodes).filter(node => node.node_type === NodeType.START)
      return startNodes.length >= 1
    },
    { message: '必须至少包含一个START类型的节点' }
  ),
  edges: z.array(treeEdgeConfigSchema)
})

// 工作流更新验证
export const workflowUpdateSchema = z.object({
  name: z.string().min(1, '工作流名称不能为空').max(200, '工作流名称不能超过200字符').optional(),
  description: z.string().max(1000, '工作流描述不能超过1000字符').optional(),
  version: z.string().min(1, '版本号不能为空').max(50, '版本号不能超过50字符').optional(),
  nodes: z.record(z.string(), treeNodeConfigSchema).optional(),
  edges: z.array(treeEdgeConfigSchema).optional(),
  status: z.nativeEnum(WorkflowStatus).optional()
})

// 快速创建工作流表单验证（简化版）
export const quickWorkflowCreateSchema = z.object({
  name: z.string().min(1, '工作流名称不能为空').max(200, '工作流名称不能超过200个字符'),
  description: z.string().min(1, '工作流描述不能为空').max(1000, '工作流描述不能超过1000个字符'),
})

// 导出类型
export type WorkflowCreateFormValues = z.infer<typeof workflowCreateSchema>
export type WorkflowUpdateFormValues = z.infer<typeof workflowUpdateSchema>
export type QuickWorkflowCreateFormValues = z.infer<typeof quickWorkflowCreateSchema>
export type TreeNodeConfigFormValues = z.infer<typeof treeNodeConfigSchema>
export type TreeEdgeConfigFormValues = z.infer<typeof treeEdgeConfigSchema>
