import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { AnimatePresence, motion } from 'framer-motion'
import { Filter, Grid, List, Plus, Search } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { type WorkflowListItem, WorkflowStatus } from '@/types/workflow'

import { useDeleteWorkflow, useRunWorkflow, useWorkflows } from '../hooks'

import { CreateWorkflowDialog } from './create-workflow-dialog'
import { WorkflowCard } from './workflow-card'
import { WorkflowEmptyState } from './workflow-empty-state'
import { WorkflowSidebar } from './workflow-sidebar'

export function WorkflowsPage() {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<WorkflowStatus | 'all'>('all')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [showCreateDialog, setShowCreateDialog] = useState(false)

  // 获取工作流列表
  const { data: workflowsData, isLoading, error } = useWorkflows({
    status_filter: statusFilter === 'all' ? undefined : statusFilter,
    limit: 50
  })

  const workflows = workflowsData?.items || []

  // 获取操作hooks
  const deleteWorkflowMutation = useDeleteWorkflow()
  const runWorkflowMutation = useRunWorkflow()

  // 过滤工作流
  const filteredWorkflows = workflows.filter(workflow =>
    workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    workflow.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleEditWorkflow = (workflow: WorkflowListItem) => {
    navigate({ to: `/edit/${workflow.id}` })
  }

  const handleRunWorkflow = (workflow: WorkflowListItem) => {
    runWorkflowMutation.mutate(workflow.id)
  }

  const handleDeleteWorkflow = (workflow: WorkflowListItem) => {
    deleteWorkflowMutation.mutate(workflow.id)
  }

  const handleCreateWorkflow = () => {
    setShowCreateDialog(true)
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.3,
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3,
        ease: 'easeOut'
      }
    }
  }

  return (
    <div className="flex h-screen bg-background">
      {/* 侧边栏 */}
      <WorkflowSidebar />

      {/* 主内容区域 */}
      <div className="flex-1 ml-72 flex flex-col">
        {/* 头部工具栏 */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
        >
          <div className="flex items-center justify-between p-6">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-foreground">工作流</h1>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="搜索工作流..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-9 w-64"
                  />
                </div>
                <Select value={statusFilter} onValueChange={(value: any) => setStatusFilter(value)}>
                  <SelectTrigger className="w-32">
                    <Filter className="h-4 w-4 mr-2" />
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部</SelectItem>
                    <SelectItem value={WorkflowStatus.ACTIVE}>活跃</SelectItem>
                    <SelectItem value={WorkflowStatus.DRAFT}>草稿</SelectItem>
                    <SelectItem value={WorkflowStatus.INACTIVE}>已停用</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* 视图切换 */}
              <div className="flex items-center border border-border rounded-lg p-1">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                  className="h-7 w-7 p-0"
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className="h-7 w-7 p-0"
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>

              <Button onClick={handleCreateWorkflow} className="gap-2">
                <Plus className="h-4 w-4" />
                新建工作流
              </Button>
            </div>
          </div>
        </motion.div>

        {/* 内容区域 */}
        <div className="flex-1 overflow-auto">
          <div className="p-6">
            {isLoading ? (
              <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                className={cn(
                  viewMode === 'grid'
                    ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
                    : 'space-y-4'
                )}
              >
                {Array.from({ length: 8 }).map((_, i) => (
                  <motion.div key={i} variants={itemVariants}>
                    <Skeleton className="h-64 w-full rounded-lg" />
                  </motion.div>
                ))}
              </motion.div>
            ) : error ? (
              <div className="flex items-center justify-center h-64">
                <p className="text-muted-foreground">加载工作流列表失败</p>
              </div>
            ) : filteredWorkflows.length === 0 ? (
              workflows.length === 0 ? (
                <WorkflowEmptyState onCreateWorkflow={handleCreateWorkflow} />
              ) : (
                <div className="flex items-center justify-center h-64">
                  <p className="text-muted-foreground">没有找到匹配的工作流</p>
                </div>
              )
            ) : (
              <AnimatePresence mode="wait">
                <motion.div
                  key={viewMode}
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                  exit="hidden"
                  className={cn(
                    viewMode === 'grid'
                      ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
                      : 'space-y-4'
                  )}
                >
                  {filteredWorkflows.map((workflow) => (
                    <motion.div
                      key={workflow.id}
                      variants={itemVariants}
                      layout
                    >
                      <WorkflowCard
                        workflow={workflow}
                        onEdit={handleEditWorkflow}
                        onRun={handleRunWorkflow}
                        onDelete={handleDeleteWorkflow}
                      />
                    </motion.div>
                  ))}
                </motion.div>
              </AnimatePresence>
            )}
          </div>
        </div>
      </div>

      {/* 创建工作流对话框 */}
      <CreateWorkflowDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
      />
    </div>
  )
}