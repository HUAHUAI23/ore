import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  X, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Pause,
  Play,
  RotateCcw,
  Calendar,
  TrendingUp
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import { useWorkflowExecutions } from '../hooks'
import { ExecutionStatus, type WorkflowExecutionListItem } from '@/types/workflow'

import { WorkflowExecutionDialog } from './workflow-execution-dialog'

interface WorkflowExecutionSidebarProps {
  workflowId: number
  isOpen: boolean
  onClose: () => void
}

export function WorkflowExecutionSidebar({ 
  workflowId, 
  isOpen, 
  onClose 
}: WorkflowExecutionSidebarProps) {
  const [selectedExecution, setSelectedExecution] = useState<number | null>(null)

  // 获取执行历史
  const { data: executionsData, isLoading } = useWorkflowExecutions(workflowId, {
    limit: 50
  })

  const executions = executionsData?.items || []

  const getStatusConfig = (status: ExecutionStatus) => {
    switch (status) {
      case ExecutionStatus.PENDING:
        return {
          icon: Clock,
          label: '等待中',
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-100',
          borderColor: 'border-yellow-200'
        }
      case ExecutionStatus.RUNNING:
        return {
          icon: Play,
          label: '运行中',
          color: 'text-blue-600',
          bgColor: 'bg-blue-100',
          borderColor: 'border-blue-200'
        }
      case ExecutionStatus.COMPLETED:
        return {
          icon: CheckCircle,
          label: '已完成',
          color: 'text-green-600',
          bgColor: 'bg-green-100',
          borderColor: 'border-green-200'
        }
      case ExecutionStatus.FAILED:
        return {
          icon: XCircle,
          label: '失败',
          color: 'text-red-600',
          bgColor: 'bg-red-100',
          borderColor: 'border-red-200'
        }
      case ExecutionStatus.CANCELLED:
        return {
          icon: Pause,
          label: '已取消',
          color: 'text-gray-600',
          bgColor: 'bg-gray-100',
          borderColor: 'border-gray-200'
        }
      default:
        return {
          icon: Clock,
          label: '未知',
          color: 'text-gray-600',
          bgColor: 'bg-gray-100',
          borderColor: 'border-gray-200'
        }
    }
  }

  const calculateProgress = (execution: WorkflowExecutionListItem) => {
    if (execution.total_nodes === 0) return 0
    return (execution.completed_nodes / execution.total_nodes) * 100
  }

  const sidebarVariants = {
    hidden: { x: '100%', opacity: 0 },
    visible: { 
      x: 0, 
      opacity: 1,
      transition: {
        type: 'spring',
        damping: 20,
        stiffness: 300
      }
    },
    exit: { 
      x: '100%', 
      opacity: 0,
      transition: {
        duration: 0.2
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, x: 20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.3,
        ease: 'easeOut'
      }
    }
  }

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            variants={sidebarVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="fixed right-0 top-0 h-screen w-80 bg-card border-l border-border shadow-xl z-50"
          >
            <div className="flex flex-col h-full">
              {/* 头部 */}
              <div className="flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-primary" />
                  <h2 className="font-semibold text-foreground">执行历史</h2>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                  className="h-8 w-8 p-0"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>

              {/* 统计信息 */}
              <div className="p-4 border-b border-border bg-muted/30">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-foreground">
                      {executions.length}
                    </div>
                    <div className="text-xs text-muted-foreground">总执行次数</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {executions.filter(e => e.status === ExecutionStatus.COMPLETED).length}
                    </div>
                    <div className="text-xs text-muted-foreground">成功次数</div>
                  </div>
                </div>
              </div>

              {/* 执行列表 */}
              <ScrollArea className="flex-1">
                <div className="p-4 space-y-3">
                  {isLoading ? (
                    Array.from({ length: 5 }).map((_, i) => (
                      <motion.div
                        key={i}
                        variants={itemVariants}
                        initial="hidden"
                        animate="visible"
                        transition={{ delay: i * 0.1 }}
                        className="space-y-2"
                      >
                        <Skeleton className="h-20 w-full rounded-lg" />
                      </motion.div>
                    ))
                  ) : executions.length === 0 ? (
                    <div className="text-center py-8">
                      <RotateCcw className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                      <p className="text-muted-foreground">暂无执行记录</p>
                    </div>
                  ) : (
                    executions.map((execution, index) => {
                      const statusConfig = getStatusConfig(execution.status)
                      const StatusIcon = statusConfig.icon
                      const progress = calculateProgress(execution)

                      return (
                        <motion.div
                          key={execution.id}
                          variants={itemVariants}
                          initial="hidden"
                          animate="visible"
                          transition={{ delay: index * 0.05 }}
                          className={cn(
                            "p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:shadow-md",
                            statusConfig.bgColor,
                            statusConfig.borderColor
                          )}
                          onClick={() => setSelectedExecution(execution.id)}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <StatusIcon className={cn("w-4 h-4", statusConfig.color)} />
                              <Badge 
                                variant="secondary" 
                                className={cn("text-xs", statusConfig.bgColor, statusConfig.color)}
                              >
                                {statusConfig.label}
                              </Badge>
                            </div>
                            <div className="text-xs text-muted-foreground">
                              #{execution.id}
                            </div>
                          </div>

                          {/* 进度条 */}
                          <div className="mb-2">
                            <div className="flex items-center justify-between text-xs mb-1">
                              <span className="text-muted-foreground">
                                进度 {execution.completed_nodes}/{execution.total_nodes}
                              </span>
                              <span className="text-muted-foreground">
                                {Math.round(progress)}%
                              </span>
                            </div>
                            <Progress 
                              value={progress} 
                              className="h-1.5"
                            />
                          </div>

                          {/* 时间信息 */}
                          <div className="space-y-1">
                            {execution.started_at && (
                              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                <Calendar className="w-3 h-3" />
                                <span>
                                  开始于 {formatDistanceToNow(new Date(execution.started_at), { 
                                    addSuffix: true, 
                                    locale: zhCN 
                                  })}
                                </span>
                              </div>
                            )}
                            
                            {execution.completed_at && (
                              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                <Clock className="w-3 h-3" />
                                <span>
                                  完成于 {formatDistanceToNow(new Date(execution.completed_at), { 
                                    addSuffix: true, 
                                    locale: zhCN 
                                  })}
                                </span>
                              </div>
                            )}
                          </div>

                          {/* 失败节点提示 */}
                          {execution.failed_nodes > 0 && (
                            <div className="mt-2 text-xs text-red-600">
                              {execution.failed_nodes} 个节点执行失败
                            </div>
                          )}
                        </motion.div>
                      )
                    })
                  )}
                </div>
              </ScrollArea>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 执行详情对话框 */}
      <WorkflowExecutionDialog
        executionId={selectedExecution}
        open={!!selectedExecution}
        onOpenChange={(open) => {
          if (!open) setSelectedExecution(null)
        }}
      />
    </>
  )
}