import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type {
  Connection,
  EdgeChange,
  EdgeTypes,
  NodeChange,
  NodeTypes,
} from '@xyflow/react'
import {
  applyEdgeChanges,
  applyNodeChanges,
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useReactFlow,
} from '@xyflow/react'
import { motion } from 'framer-motion'

import { cn } from '@/lib/utils'
import { useWorkflowEditorStore } from '@/stores/workflow-editor'
import type { WorkflowResponse, ConditionConfig } from '@/types/workflow'
import { NodeType } from '@/types/workflow'

import { WorkflowEdge } from './workflow-edge'
import { WorkflowNode } from './workflow-node'
import { WorkflowSelectionToolbar } from './workflow-selection-toolbar'

import '@xyflow/react/dist/style.css'

interface WorkflowNodeData extends Record<string, unknown> {
  label: string
  description: string
  prompt: string
  nodeType: NodeType
  conditions?: ConditionConfig[]
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
  const { nodes, edges, setNodes, setEdges, removeNodes } = useWorkflowEditorStore()
  // React Flow 相关 hooks
  const { screenToFlowPosition } = useReactFlow()
  const reactFlowWrapper = useRef<HTMLDivElement>(null)

  // 选中的节点状态
  const [selectedNodeIds, setSelectedNodeIds] = useState<string[]>([])

  // 自定义节点类型
  const nodeTypes: NodeTypes = useMemo(() => ({
    workflowNode: WorkflowNode as never,
  }), [])

  // 自定义边类型
  const edgeTypes: EdgeTypes = useMemo(() => ({
    workflowEdge: WorkflowEdge as never,
  }), [])

  const onConnect = useCallback((params: Connection) => {
    let condition = null
    
    // 检查是否从条件连接点连出
    if (params.sourceHandle && params.sourceHandle.startsWith('condition-')) {
      const conditionIndex = parseInt(params.sourceHandle.split('-')[1])
      const sourceNode = nodes.find(n => n.id === params.source)
      if (sourceNode && (sourceNode.data as any).conditions) {
        const conditions = (sourceNode.data as any).conditions as ConditionConfig[]
        if (conditions[conditionIndex]) {
          condition = conditions[conditionIndex]
        }
      }
    }
    
    const newEdge = {
      ...params,
      id: `edge-${Date.now()}`,
      type: 'workflowEdge',
      data: {
        condition,
        inputConfig: {
          include_prompt: true,
          include_previous_output: true,
        },
      },
    }
    setEdges([...edges, newEdge])
  }, [setEdges, edges, nodes])

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
        conditions: [],
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

  // 处理选择变化
  const handleSelectionChange = useCallback((selection: { nodes: { id: string }[] }) => {
    const nodeIds = selection.nodes.map(node => node.id)
    setSelectedNodeIds(nodeIds)
  }, [])

  // 删除选中的节点
  const handleDeleteNodes = useCallback((nodeIds: string[]) => {
    removeNodes(nodeIds)
    setSelectedNodeIds([])
  }, [removeNodes])

  // 键盘事件处理 - 只在工作流编辑器容器内生效
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // 检查焦点是否在工作流编辑器内，或者没有其他输入元素获得焦点
      const activeElement = document.activeElement
      const isInputElement = activeElement && (
        activeElement.tagName === 'INPUT' ||
        activeElement.tagName === 'TEXTAREA' ||
        activeElement.tagName === 'SELECT' ||
        activeElement.hasAttribute('contenteditable')
      )

      // 如果有输入元素获得焦点，不处理删除键
      if (isInputElement) {
        return
      }

      if ((event.key === 'Delete' || event.key === 'Backspace') && selectedNodeIds.length > 0) {
        event.preventDefault()
        handleDeleteNodes(selectedNodeIds)
      }
    }

    // 只在工作流编辑器容器上添加事件监听器
    const container = reactFlowWrapper.current
    if (container) {
      container.addEventListener('keydown', handleKeyDown)
      // 确保容器可以获得焦点
      container.tabIndex = -1
      return () => {
        container.removeEventListener('keydown', handleKeyDown)
      }
    }
  }, [selectedNodeIds, handleDeleteNodes])



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
        onSelectionChange={handleSelectionChange}
        fitView
        fitViewOptions={{
          padding: 0.2,
        }}
        className="bg-background"
        deleteKeyCode={null}
        multiSelectionKeyCode={["Meta", "Ctrl"]}
        panOnDrag={true}
        selectionOnDrag={false}
        snapToGrid={false}
        panOnScroll={false}
        selectionKeyCode={null}
        selectNodesOnDrag={false}
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

      {/* 选择工具栏 */}
      <WorkflowSelectionToolbar
        selectedNodes={selectedNodeIds}
        onDeleteNodes={handleDeleteNodes}
        onEditNode={(nodeId) => {
          const node = nodes.find(n => n.id === nodeId)
          if (node) {
            onEditNode?.(nodeId, node.data as WorkflowNodeData)
          }
        }}
      />
    </motion.div>
  )
}