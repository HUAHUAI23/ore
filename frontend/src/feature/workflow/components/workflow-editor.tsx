import React, { useCallback, useMemo, useRef } from 'react'
import type {
  Connection,
  Edge,
  EdgeTypes,
  Node,
  NodeTypes,
} from '@xyflow/react'
import {
  addEdge,
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from '@xyflow/react'
import { motion } from 'framer-motion'

import { cn } from '@/lib/utils'
import type { WorkflowResponse } from '@/types/workflow'
import { NodeType } from '@/types/workflow'

import { WorkflowEdge } from './workflow-edge'
import { WorkflowNode } from './workflow-node'

import '@xyflow/react/dist/style.css'

interface WorkflowNodeData extends Record<string, unknown> {
  label: string
  description: string
  prompt: string
  nodeType: NodeType
}

interface WorkflowEditorProps {
  workflow?: WorkflowResponse
  onNodesChange?: (nodes: Node[]) => void
  onEdgesChange?: (edges: Edge[]) => void
  onAddNode?: (nodeType: NodeType) => void
  onEditNode?: (nodeId: string, nodeData: WorkflowNodeData) => void
  className?: string
}

export function WorkflowEditor({
  workflow,
  onNodesChange,
  onEdgesChange,
  onAddNode: _onAddNode,
  onEditNode,
  className
}: WorkflowEditorProps) {
  // 转换工作流数据为React Flow格式
  const initialNodes = useMemo(() => {
    if (!workflow?.nodes) return []

    return Object.values(workflow.nodes).map((node: unknown, index) => {
      const nodeData = node as Record<string, unknown>
      return {
        id: nodeData.id as string,
        type: 'workflowNode',
        position: {
          x: index * 200,
          y: nodeData.node_type === NodeType.START ? 0 : 100 + (index * 100)
        },
        data: {
          label: nodeData.name as string,
          description: nodeData.description as string,
          prompt: nodeData.prompt as string,
          nodeType: nodeData.node_type as NodeType,
        },
      }
    })
  }, [workflow?.nodes])

  const initialEdges = useMemo(() => {
    if (!workflow?.edges) return []

    return workflow.edges.map((edge: unknown, index) => {
      const edgeData = edge as Record<string, unknown>
      return {
        id: `edge-${index}`,
        source: edgeData.from_node as string,
        target: edgeData.to_node as string,
        type: 'workflowEdge',
        data: {
          condition: edgeData.condition,
          inputConfig: edgeData.input_config,
        },
      }
    })
  }, [workflow?.edges])

  const [nodes, setNodes, onNodesChangeInternal] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChangeInternal] = useEdgesState(initialEdges)
  const { screenToFlowPosition } = useReactFlow()
  const reactFlowWrapper = useRef<HTMLDivElement>(null)

  // 自定义节点类型
  const nodeTypes: NodeTypes = useMemo(() => ({
    workflowNode: WorkflowNode as never,
  }), [])

  // 自定义边类型
  const edgeTypes: EdgeTypes = useMemo(() => ({
    workflowEdge: WorkflowEdge as never,
  }), [])

  const onConnect = useCallback((params: Connection) => {
    setEdges((eds) => addEdge({
      ...params,
      type: 'workflowEdge',
      data: {
        condition: null,
        inputConfig: {
          include_prompt: true,
          include_previous_output: true,
        },
      },
    }, eds))
  }, [setEdges])

  // 创建新节点
  const createNode = useCallback((nodeType: NodeType, position?: { x: number; y: number }) => {
    const id = `node-${Date.now()}`
    const defaultPosition = position || { x: 250, y: 250 }

    const getNodeDefaults = (type: NodeType) => {
      switch (type) {
        case NodeType.START:
          return {
            label: '开始节点',
            description: '工作流的起始点',
            prompt: '',
          }
        case NodeType.INTERMEDIATE:
          return {
            label: '处理节点',
            description: '执行具体的处理逻辑',
            prompt: '请输入处理逻辑的提示词...',
          }
        case NodeType.LEAF:
          return {
            label: '结束节点',
            description: '工作流的终点',
            prompt: '',
          }
        default:
          return {
            label: '未知节点',
            description: '',
            prompt: '',
          }
      }
    }

    const nodeDefaults = getNodeDefaults(nodeType)

    const newNode = {
      id,
      type: 'workflowNode' as const,
      position: defaultPosition,
      data: {
        ...nodeDefaults,
        nodeType,
      },
    }

    setNodes((nds) => [...nds, newNode])
    return newNode
  }, [setNodes])

  // 处理拖拽放置
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault()

    const nodeType = event.dataTransfer.getData('application/reactflow') as NodeType

    if (!nodeType) {
      return
    }

    const position = screenToFlowPosition({
      x: event.clientX,
      y: event.clientY,
    })

    createNode(nodeType, position)
  }, [screenToFlowPosition, createNode])

  // 处理节点变化
  const handleNodesChange = useCallback((changes: unknown) => {
    onNodesChangeInternal(changes as never)
  }, [onNodesChangeInternal])

  // 处理边变化
  const handleEdgesChange = useCallback((changes: unknown) => {
    onEdgesChangeInternal(changes as never)
  }, [onEdgesChangeInternal])

  // 当节点或边发生变化时，通知父组件
  React.useEffect(() => {
    onNodesChange?.(nodes)
  }, [nodes, onNodesChange])

  React.useEffect(() => {
    onEdgesChange?.(edges)
  }, [edges, onEdgesChange])



  return (
    <motion.div
      ref={reactFlowWrapper}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className={cn("h-full w-full", className)}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onConnect={onConnect}
        onDragOver={onDragOver}
        onDrop={onDrop}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onNodeDoubleClick={(_, node) => {
          onEditNode?.(node.id, node.data as WorkflowNodeData)
        }}
        fitView
        fitViewOptions={{
          padding: 0.2,
        }}
        className="bg-background"
        deleteKeyCode={["Backspace", "Delete"]}
        multiSelectionKeyCode={["Meta", "Ctrl"]}
        panOnDrag={[1, 2]}
        selectionOnDrag
        snapToGrid
        snapGrid={[20, 20]}
      >
        <Background
          color="#e2e8f0"
          gap={20}
          size={1}
        />
        <Controls
          className="bg-card border border-border rounded-lg shadow-sm"
          showInteractive={true}
          showZoom={true}
          showFitView={true}
        />
        <MiniMap
          className="bg-card border border-border rounded-lg shadow-sm"
          nodeColor={(node) => {
            switch (node.data.nodeType) {
              case NodeType.START:
                return '#10b981' // green
              case NodeType.INTERMEDIATE:
                return '#3b82f6' // blue
              case NodeType.LEAF:
                return '#f59e0b' // amber
              default:
                return '#6b7280' // gray
            }
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
          pannable
          zoomable
        />
      </ReactFlow>
    </motion.div>
  )
}