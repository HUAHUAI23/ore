/**
 * 工作流编辑器状态管理 Store
 * 使用 Zustand 管理工作流编辑过程中的状态
 */

import type { Edge, Node } from '@xyflow/react'
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

import type { NodeType, TreeNodeConfig,WorkflowResponse } from '@/types/workflow'

// 智能布局算法
function createWorkflowLayout(nodes: any[], edges: any[]) {
  // 创建节点图结构
  const nodeMap = new Map(nodes.map(node => [node.id, node]))
  const adjacencyMap = new Map<string, string[]>()
  const inDegreeMap = new Map<string, number>()
  
  // 初始化邻接表和入度
  nodes.forEach(node => {
    adjacencyMap.set(node.id, [])
    inDegreeMap.set(node.id, 0)
  })
  
  // 构建图结构
  edges.forEach(edge => {
    const from = edge.from_node
    const to = edge.to_node
    if (adjacencyMap.has(from) && adjacencyMap.has(to)) {
      adjacencyMap.get(from)!.push(to)
      inDegreeMap.set(to, (inDegreeMap.get(to) || 0) + 1)
    }
  })
  
  // 拓扑排序分层
  const layers: string[][] = []
  const visited = new Set<string>()
  const queue: string[] = []
  
  // 找到所有起始节点（入度为0的节点）
  nodes.forEach(node => {
    if (inDegreeMap.get(node.id) === 0) {
      queue.push(node.id)
    }
  })
  
  // 如果没有入度为0的节点，找START类型节点
  if (queue.length === 0) {
    const startNode = nodes.find(node => node.node_type === 'START')
    if (startNode) {
      queue.push(startNode.id)
    }
  }
  
  // 分层布局
  while (queue.length > 0) {
    const currentLayer: string[] = []
    const nextQueue: string[] = []
    
    while (queue.length > 0) {
      const nodeId = queue.shift()!
      if (!visited.has(nodeId)) {
        visited.add(nodeId)
        currentLayer.push(nodeId)
        
        // 添加下一层节点
        const children = adjacencyMap.get(nodeId) || []
        children.forEach(childId => {
          const newInDegree = (inDegreeMap.get(childId) || 0) - 1
          inDegreeMap.set(childId, newInDegree)
          if (newInDegree === 0 && !visited.has(childId)) {
            nextQueue.push(childId)
          }
        })
      }
    }
    
    if (currentLayer.length > 0) {
      layers.push(currentLayer)
      queue.push(...nextQueue)
    }
  }
  
  // 处理剩余未访问的节点（循环依赖等）
  const unvisitedNodes = nodes.filter(node => !visited.has(node.id))
  if (unvisitedNodes.length > 0) {
    layers.push(unvisitedNodes.map(node => node.id))
  }
  
  // 计算位置
  const nodeSpacing = { x: 350, y: 150 }
  const startOffset = { x: 100, y: 100 }
  
  const layoutNodes: Array<any & { position: { x: number; y: number } }> = []
  
  layers.forEach((layer, layerIndex) => {
    const layerY = startOffset.y + layerIndex * nodeSpacing.y
    const layerStartX = startOffset.x - ((layer.length - 1) * nodeSpacing.x) / 2
    
    layer.forEach((nodeId, nodeIndex) => {
      const node = nodeMap.get(nodeId)
      if (node) {
        layoutNodes.push({
          ...node,
          position: {
            x: layerStartX + nodeIndex * nodeSpacing.x,
            y: layerY
          }
        })
      }
    })
  })
  
  return layoutNodes
}

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
  removeNodes: (nodeIds: string[]) => void
  
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
          // 转换后端数据为 React Flow 格式，使用更智能的布局算法
          const nodeArray = Object.values(workflow.nodes) as any[]
          const edges = workflow.edges || []
          
          // 创建布局映射
          const layoutNodes = createWorkflowLayout(nodeArray, edges)
          
          const nodes = layoutNodes.map((node) => ({
            id: node.id,
            type: 'workflowNode',
            position: node.position,
            data: {
              label: node.name,
              description: node.description,
              prompt: node.prompt,
              nodeType: node.node_type as NodeType,
              conditions: node.conditions || [],
            },
          }))

          const workflowEdges = (workflow.edges || []).map((edge: any, index) => ({
            id: `edge-${index}`,
            source: edge.from_node,
            target: edge.to_node,
            type: 'workflowEdge',
            data: {
              condition: edge.condition,
              inputConfig: edge.input_config,
            },
          }))

          set({ nodes, edges: workflowEdges })
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
                conditions: nodeData.conditions || node.data.conditions || [],
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
            conditions: [],
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

      // 批量删除节点
      removeNodes: (nodeIds) => {
        const { nodes, edges } = get()
        const nodeIdSet = new Set(nodeIds)
        
        // 过滤掉要删除的节点
        const updatedNodes = nodes.filter(node => !nodeIdSet.has(node.id))
        
        // 过滤掉与删除节点相关的边
        const updatedEdges = edges.filter(edge => 
          !nodeIdSet.has(edge.source) && !nodeIdSet.has(edge.target)
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
            conditions: (node.data?.conditions as any) || [],
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