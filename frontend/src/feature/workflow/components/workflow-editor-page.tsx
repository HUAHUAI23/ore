import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import type { Edge, Node } from '@xyflow/react'
import { ReactFlowProvider } from '@xyflow/react'
import { motion } from 'framer-motion'
import {
  ArrowLeft,
  History,
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  Play,
  Save,
  Settings,
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { NodeType, WorkflowStatus } from '@/types/workflow'
import type { TreeNodeConfigFormValues, WorkflowUpdateFormValues } from '@/validation/workflow'

import { useRunWorkflow, useUpdateWorkflow, useWorkflow } from '../hooks'

import { NodeEditDialog } from './node-edit-dialog'
import { NodePanel } from './node-panel'
import { WorkflowEditor } from './workflow-editor'
import { WorkflowExecutionSidebar } from './workflow-execution-sidebar'
import { WorkflowSettingsDialog } from './workflow-settings-dialog'

interface WorkflowEditorPageProps {
  workflowId: number
}

export function WorkflowEditorPage({ workflowId }: WorkflowEditorPageProps) {
  const navigate = useNavigate()
  const [showExecutionSidebar, setShowExecutionSidebar] = useState(false)
  const [showNodePanel, setShowNodePanel] = useState(true)
  const [currentNodes, setCurrentNodes] = useState<Node[]>([])
  const [currentEdges, setCurrentEdges] = useState<Edge[]>([])

  // 对话框状态
  const [nodeEditDialog, setNodeEditDialog] = useState<{
    open: boolean
    nodeData?: {
      id: string
      label: string
      description: string
      prompt: string
      nodeType: NodeType
    }
  }>({ open: false })

  const [settingsDialog, setSettingsDialog] = useState(false)

  // 获取工作流数据
  const { data: workflow, isLoading, error } = useWorkflow(workflowId)
  const updateWorkflowMutation = useUpdateWorkflow(workflowId)
  const runWorkflowMutation = useRunWorkflow(workflowId)

  const handleBack = () => {
    navigate({ to: '/workflows' })
  }

  const handleSave = () => {
    if (!workflow) return

    // 如果有节点数据，则保存；否则保存当前工作流状态
    if (currentNodes.length > 0) {
      // 转换节点数据为后端格式
      const nodes = currentNodes.reduce((acc, node) => {
        acc[node.id] = {
          id: node.id,
          name: (node.data?.label as string) || node.id,
          description: (node.data?.description as string) || '',
          prompt: (node.data?.prompt as string) || '',
          node_type: (node.data?.nodeType as NodeType) || NodeType.INTERMEDIATE,
        }
        return acc
      }, {} as Record<string, {
        id: string
        name: string
        description: string
        prompt: string
        node_type: NodeType
      }>)

      // 转换边数据为后端格式
      const edges = currentEdges.map((edge) => ({
        from_node: edge.source,
        to_node: edge.target,
        condition: (edge.data?.condition as any) || null,
        input_config: (edge.data?.inputConfig as any) || {
          include_prompt: true,
          include_previous_output: true,
        },
      }))

      updateWorkflowMutation.mutate({
        nodes,
        edges,
      })
    } else {
      // 如果没有编辑器数据，只更新基本信息
      updateWorkflowMutation.mutate({})
    }
  }

  const handleRun = () => {
    runWorkflowMutation.mutate(workflowId)
  }

  // 处理添加节点
  const handleAddNode = (_nodeType: NodeType) => {
    // 添加节点逻辑已在WorkflowEditor组件中实现
  }

  // 处理节点编辑
  const handleNodeEdit = (nodeId: string, nodeData: {
    label: string
    description: string
    prompt: string
    nodeType: NodeType
  }) => {
    setNodeEditDialog({
      open: true,
      nodeData: {
        id: nodeId,
        label: nodeData.label,
        description: nodeData.description,
        prompt: nodeData.prompt,
        nodeType: nodeData.nodeType,
      }
    })
  }

  // 保存节点配置
  const handleSaveNodeConfig = async (_data: TreeNodeConfigFormValues) => {
    // TODO: 实现节点配置更新逻辑
    // 这里应该调用API更新节点配置
    setNodeEditDialog({ open: false })
  }

  // 保存工作流设置
  const handleSaveWorkflowSettings = async (_data: WorkflowUpdateFormValues) => {
    updateWorkflowMutation.mutate(_data)
    setSettingsDialog(false)
  }

  const getStatusConfig = (status: WorkflowStatus) => {
    switch (status) {
      case WorkflowStatus.ACTIVE:
        return { label: '活跃', className: 'bg-green-100 text-green-800' }
      case WorkflowStatus.INACTIVE:
        return { label: '已停用', className: 'bg-gray-100 text-gray-800' }
      case WorkflowStatus.DRAFT:
        return { label: '草稿', className: 'bg-blue-100 text-blue-800' }
      default:
        return { label: '未知', className: 'bg-gray-100 text-gray-800' }
    }
  }

  if (isLoading) {
    return (
      <div className="h-screen flex flex-col">
        <div className="border-b border-border p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Skeleton className="h-8 w-8" />
              <Skeleton className="h-6 w-48" />
            </div>
            <div className="flex items-center gap-2">
              <Skeleton className="h-8 w-16" />
              <Skeleton className="h-8 w-16" />
            </div>
          </div>
        </div>
        <div className="flex-1">
          <Skeleton className="h-full w-full" />
        </div>
      </div>
    )
  }

  if (error || !workflow) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground mb-4">加载工作流失败</p>
          <Button onClick={handleBack} variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            返回列表
          </Button>
        </div>
      </div>
    )
  }

  const statusConfig = getStatusConfig(workflow.status)

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* 头部工具栏 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
      >
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBack}
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              返回
            </Button>

            <Separator orientation="vertical" className="h-6" />

            <div className="flex items-center gap-3">
              <div>
                <h1 className="text-lg font-semibold text-foreground">
                  {workflow.name}
                </h1>
                <p className="text-sm text-muted-foreground">
                  {workflow.description}
                </p>
              </div>
              <Badge className={statusConfig.className}>
                {statusConfig.label}
              </Badge>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowNodePanel(!showNodePanel)}
              className="gap-2"
            >
              {showNodePanel ? (
                <PanelLeftClose className="w-4 h-4" />
              ) : (
                <PanelLeftOpen className="w-4 h-4" />
              )}
              节点面板
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowExecutionSidebar(!showExecutionSidebar)}
              className="gap-2"
            >
              <History className="w-4 h-4" />
              执行历史
              {showExecutionSidebar ? (
                <PanelRightClose className="w-4 h-4" />
              ) : (
                <PanelRightOpen className="w-4 h-4" />
              )}
            </Button>

            <Separator orientation="vertical" className="h-6" />

            <Button
              variant="outline"
              size="sm"
              onClick={handleSave}
              disabled={updateWorkflowMutation.isPending}
              className="gap-2"
            >
              <Save className="w-4 h-4" />
              {updateWorkflowMutation.isPending ? '保存中...' : '保存'}
            </Button>

            <Button
              size="sm"
              onClick={handleRun}
              disabled={runWorkflowMutation.isPending || workflow.status !== WorkflowStatus.ACTIVE}
              className="gap-2"
            >
              <Play className="w-4 h-4" />
              {runWorkflowMutation.isPending ? '运行中...' : '运行'}
            </Button>

            <Button
              variant="ghost"
              size="sm"
              className="gap-2"
              onClick={() => setSettingsDialog(true)}
            >
              <Settings className="w-4 h-4" />
              设置
            </Button>
          </div>
        </div>
      </motion.div>

      {/* 主内容区域 */}
      <div className="flex-1 flex">
        {/* 节点面板 */}
        {showNodePanel && (
          <NodePanel
            onAddNode={handleAddNode}
          />
        )}

        {/* 工作流编辑器 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className={`flex-1 transition-all duration-300 ${showNodePanel ? 'ml-0' : ''
            } ${showExecutionSidebar ? 'mr-80' : ''}`}
        >
          <ReactFlowProvider>
            <WorkflowEditor
              workflow={workflow}
              onNodesChange={(nodes) => {
                setCurrentNodes(nodes)
              }}
              onEdgesChange={(edges) => {
                setCurrentEdges(edges)
              }}
              onAddNode={handleAddNode}
              onEditNode={handleNodeEdit}
            />
          </ReactFlowProvider>
        </motion.div>

        {/* 执行历史侧边栏 */}
        <WorkflowExecutionSidebar
          workflowId={workflowId}
          isOpen={showExecutionSidebar}
          onClose={() => setShowExecutionSidebar(false)}
        />
      </div>

      {/* 节点编辑对话框 */}
      <NodeEditDialog
        open={nodeEditDialog.open}
        onOpenChange={(open) => setNodeEditDialog({ ...nodeEditDialog, open })}
        nodeData={nodeEditDialog.nodeData}
        onSave={handleSaveNodeConfig}
      />

      {/* 工作流设置对话框 */}
      <WorkflowSettingsDialog
        open={settingsDialog}
        onOpenChange={setSettingsDialog}
        workflowData={workflow ? {
          id: workflow.id,
          name: workflow.name,
          description: workflow.description,
          version: workflow.version,
          status: workflow.status,
          type: workflow.type,
        } : undefined}
        onSave={handleSaveWorkflowSettings}
      />
    </div>
  )
}