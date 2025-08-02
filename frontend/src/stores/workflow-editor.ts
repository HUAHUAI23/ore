/**
 * 工作流编辑器状态管理 Store
 * 使用 Zustand 管理工作流编辑过程中的状态
 */

import type { Edge, Node } from '@xyflow/react'
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

import type { NodeType, TreeNodeConfig,WorkflowResponse } from '@/types/workflow'

interface WorkflowEditorState {
  // 当前工作流数据
  workflow: WorkflowResponse | null
  
  // React Flow 节点和边
  nodes: Node[]
  edges: Edge[]
  
  // 编辑状态
  hasUnsavedChanges: boolean
  isLoading: boolean
  
  
  // Actions
  setWorkflow: (workflow: WorkflowResponse | null) => void
  setNodes: (nodes: Node[]) => void
  setEdges: (edges: Edge[]) => void
  updateNode: (nodeId: string, nodeData: Partial<TreeNodeConfig>) => void
  addNode: (nodeType: NodeType, position?: { x: number; y: number }) => void
  removeNode: (nodeId: string) => void
  
  // 工具方法
  getWorkflowData: () => {
    nodes: Record<string, TreeNodeConfig>
    edges: Array<{
      from_node: string
      to_node: string
      condition?: any
      input_config: {
        include_prompt: boolean
        include_previous_output: boolean
      }
    }>
  }
  
  // 重置状态
  reset: () => void
  markAsSaved: () => void
}

export const useWorkflowEditorStore = create<WorkflowEditorState>()(
  devtools(
    (set, get) => ({
      // 初始状态
      workflow: null,
      nodes: [],
      edges: [],
      hasUnsavedChanges: false,
      isLoading: false,

      // 设置工作流数据
      setWorkflow: (workflow) => {
        set({ workflow, isLoading: false })
        
        if (workflow?.nodes) {
          // 转换后端数据为 React Flow 格式
          const nodes = Object.values(workflow.nodes).map((node: any, index) => ({
            id: node.id,
            type: 'workflowNode',
            position: {
              x: node.node_type === 'START' ? 0 : 300 + (index * 300),
              y: 100 + (index % 3) * 150 // 错列显示，避免重叠
            },
            data: {
              label: node.name,
              description: node.description,
              prompt: node.prompt,
              nodeType: node.node_type as NodeType,
            },
          }))

          const edges = (workflow.edges || []).map((edge: any, index) => ({
            id: `edge-${index}`,
            source: edge.from_node,
            target: edge.to_node,
            type: 'workflowEdge',
            data: {
              condition: edge.condition,
              inputConfig: edge.input_config,
            },
          }))

          set({ nodes, edges })
        }
      },

      // 设置节点
      setNodes: (nodes) => {
        set({ nodes, hasUnsavedChanges: true })
      },

      // 设置边
      setEdges: (edges) => {
        set({ edges, hasUnsavedChanges: true })
      },

      // 更新单个节点
      updateNode: (nodeId, nodeData) => {
        const { nodes } = get()
        const updatedNodes = nodes.map(node => {
          if (node.id === nodeId) {
            return {
              ...node,
              data: {
                ...node.data,
                label: nodeData.name || node.data.label,
                description: nodeData.description || node.data.description,
                prompt: nodeData.prompt || node.data.prompt,
                nodeType: nodeData.node_type || node.data.nodeType,
              }
            }
          }
          return node
        })
        
        set({ nodes: updatedNodes, hasUnsavedChanges: true })
      },

      // 添加节点
      addNode: (nodeType, position = { x: 100, y: 100 }) => {
        const { nodes } = get()
        const nodeId = `node-${Date.now()}`
        
        const newNode: Node = {
          id: nodeId,
          type: 'workflowNode',
          position,
          data: {
            label: `新${nodeType === 'START' ? '开始' : nodeType === 'LEAF' ? '结束' : '处理'}节点`,
            description: '',
            prompt: '',
            nodeType,
          },
        }

        set({ 
          nodes: [...nodes, newNode], 
          hasUnsavedChanges: true 
        })
      },

      // 删除节点
      removeNode: (nodeId) => {
        const { nodes, edges } = get()
        const updatedNodes = nodes.filter(node => node.id !== nodeId)
        const updatedEdges = edges.filter(edge => 
          edge.source !== nodeId && edge.target !== nodeId
        )
        
        set({ 
          nodes: updatedNodes, 
          edges: updatedEdges, 
          hasUnsavedChanges: true 
        })
      },


      // 获取工作流数据（用于保存）
      getWorkflowData: () => {
        const { nodes, edges } = get()
        
        // 转换节点数据为后端格式
        const backendNodes = nodes.reduce((acc, node) => {
          acc[node.id] = {
            id: node.id,
            name: (node.data?.label as string) || node.id,
            description: (node.data?.description as string) || '',
            prompt: (node.data?.prompt as string) || '',
            node_type: (node.data?.nodeType as NodeType) || 'INTERMEDIATE',
          }
          return acc
        }, {} as Record<string, TreeNodeConfig>)

        // 转换边数据为后端格式
        const backendEdges = edges.map((edge) => ({
          from_node: edge.source,
          to_node: edge.target,
          condition: (edge.data?.condition as any) || null,
          input_config: (edge.data?.inputConfig as any) || {
            include_prompt: true,
            include_previous_output: true,
          },
        }))

        return {
          nodes: backendNodes,
          edges: backendEdges,
        }
      },

      // 标记为已保存
      markAsSaved: () => {
        set({ hasUnsavedChanges: false })
      },

      // 重置状态
      reset: () => {
        set({
          workflow: null,
          nodes: [],
          edges: [],
          hasUnsavedChanges: false,
          isLoading: false,
        })
      },
    }),
    {
      name: 'workflow-editor-store',
    }
  )
)