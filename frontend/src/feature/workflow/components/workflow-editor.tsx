import React, { useCallback, useMemo, useRef } from 'react'
import type {
  Connection,
  EdgeTypes,
  NodeTypes,
  NodeChange,
  EdgeChange,
} from '@xyflow/react'
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useReactFlow,
  applyNodeChanges,
  applyEdgeChanges,
} from '@xyflow/react'
import { motion } from 'framer-motion'

import { cn } from '@/lib/utils'
import { useWorkflowEditorStore } from '@/stores/workflow-editor'
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
  onAddNode?: (nodeType: NodeType) => void
  onEditNode?: (nodeId: string, nodeData: WorkflowNodeData) => void
  className?: string
}

export function WorkflowEditor({
  workflow: _workflow,
  onAddNode: _onAddNode,
  onEditNode,
  className
}: WorkflowEditorProps) {
  // 使用 Zustand store
  const { nodes, edges, setNodes, setEdges } = useWorkflowEditorStore()
  // React Flow 相关 hooks
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
    const newEdge = {
      ...params,
      id: `edge-${Date.now()}`,
      type: 'workflowEdge',
      data: {
        condition: null,
        inputConfig: {
          include_prompt: true,
          include_previous_output: true,
        },
      },
    }
    setEdges([...edges, newEdge])
  }, [setEdges, edges])

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

    setNodes([...nodes, newNode])
    return newNode
  }, [setNodes, nodes])

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
  const handleNodesChange = useCallback((changes: NodeChange[]) => {
    const updatedNodes = applyNodeChanges(changes, nodes)
    setNodes(updatedNodes)
  }, [nodes, setNodes])

  // 处理边变化
  const handleEdgesChange = useCallback((changes: EdgeChange[]) => {
    const updatedEdges = applyEdgeChanges(changes, edges)
    setEdges(updatedEdges)
  }, [edges, setEdges])



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
        snapToGrid={false}
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