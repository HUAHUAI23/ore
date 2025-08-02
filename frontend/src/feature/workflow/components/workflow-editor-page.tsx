import { useEffect, useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { ReactFlowProvider } from '@xyflow/react'
import { AnimatePresence, motion } from 'framer-motion'
import {
  ArrowLeft,
  History,
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
import { useWorkflowEditorStore } from '@/stores/workflow-editor'
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

  // Zustand store
  const {
    workflow: storeWorkflow,
    hasUnsavedChanges,
    setWorkflow,
    updateNode,
    addNode,
    getWorkflowData,
    markAsSaved,
    reset
  } = useWorkflowEditorStore()

  // 获取工作流数据
  const { data: workflow, isLoading, error } = useWorkflow(workflowId)
  const updateWorkflowMutation = useUpdateWorkflow(workflowId)
  const runWorkflowMutation = useRunWorkflow(workflowId)

  // 当工作流数据加载完成时，更新 store
  useEffect(() => {
    if (workflow) {
      setWorkflow(workflow)
    }
  }, [workflow, setWorkflow])

  // 组件卸载时重置 store
  useEffect(() => {
    return () => {
      reset()
    }
  }, [reset])

  const handleBack = () => {
    navigate({ to: '/workflows' })
  }

  const handleSave = () => {
    if (!workflow) return

    // 从 Zustand store 获取最新的工作流数据
    const workflowData = getWorkflowData()

    updateWorkflowMutation.mutate(workflowData, {
      onSuccess: () => {
        // 保存成功后标记为已保存
        markAsSaved()
      }
    })
  }

  const handleRun = () => {
    runWorkflowMutation.mutate(workflowId)
  }

  // 处理添加节点
  const handleAddNode = (nodeType: NodeType) => {
    addNode(nodeType)
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
  const handleSaveNodeConfig = async (data: TreeNodeConfigFormValues) => {
    // 使用 Zustand store 更新节点数据
    updateNode(data.id, {
      name: data.name,
      description: data.description,
      prompt: data.prompt,
      node_type: data.node_type,
    })

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
              disabled={updateWorkflowMutation.isPending || !hasUnsavedChanges}
              className="gap-2"
            >
              <Save className="w-4 h-4" />
              {updateWorkflowMutation.isPending ? '保存中...' : hasUnsavedChanges ? '保存' : '已保存'}
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
      <div className="flex-1 flex relative">
        {/* 工作流编辑器 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className={`flex-1 transition-all duration-300 ${showExecutionSidebar ? 'mr-80' : ''} relative`}
        >
          <ReactFlowProvider>
            <WorkflowEditor
              workflow={storeWorkflow || undefined}
              onAddNode={handleAddNode}
              onEditNode={handleNodeEdit}
            />
          </ReactFlowProvider>

          {/* 悬浮按钮 - 打开节点面板 */}
          {!showNodePanel && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.2 }}
              className="absolute top-4 left-4 z-10"
            >
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowNodePanel(true)}
                className="gap-2 bg-background/95 backdrop-blur shadow-lg border-border/50"
              >
                <PanelLeftOpen className="w-4 h-4" />
                节点面板
              </Button>
            </motion.div>
          )}
        </motion.div>

        {/* 悬浮节点面板 */}
        <AnimatePresence>
          {showNodePanel && (
            <NodePanel
              onAddNode={handleAddNode}
              onClose={() => setShowNodePanel(false)}
            />
          )}
        </AnimatePresence>

        {/* 执行历史侧边栏 - 只在打开时渲染 */}
        {showExecutionSidebar && (
          <WorkflowExecutionSidebar
            workflowId={workflowId}
            isOpen={showExecutionSidebar}
            onClose={() => setShowExecutionSidebar(false)}
          />
        )}
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