import { motion } from 'framer-motion'
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  Pause,
  Play,
  Calendar,
  AlertTriangle,
  FileText,
  Download,
  Copy
} from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { useExecutionDetail, useCancelExecution } from '../hooks'
import { ExecutionStatus } from '@/types/workflow'

interface WorkflowExecutionDialogProps {
  executionId: number | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function WorkflowExecutionDialog({ 
  executionId, 
  open, 
  onOpenChange 
}: WorkflowExecutionDialogProps) {
  const { data: execution, isLoading } = useExecutionDetail(executionId!)
  const cancelExecutionMutation = useCancelExecution()

  if (!executionId) return null

  const getStatusConfig = (status: ExecutionStatus) => {
    switch (status) {
      case ExecutionStatus.PENDING:
        return {
          icon: Clock,
          label: '等待中',
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-100',
          description: '执行正在队列中等待'
        }
      case ExecutionStatus.RUNNING:
        return {
          icon: Play,
          label: '运行中',
          color: 'text-blue-600',
          bgColor: 'bg-blue-100',
          description: '工作流正在执行中'
        }
      case ExecutionStatus.COMPLETED:
        return {
          icon: CheckCircle,
          label: '已完成',
          color: 'text-green-600',
          bgColor: 'bg-green-100',
          description: '工作流执行成功完成'
        }
      case ExecutionStatus.FAILED:
        return {
          icon: XCircle,
          label: '执行失败',
          color: 'text-red-600',
          bgColor: 'bg-red-100',
          description: '工作流执行过程中出现错误'
        }
      case ExecutionStatus.CANCELLED:
        return {
          icon: Pause,
          label: '已取消',
          color: 'text-gray-600',
          bgColor: 'bg-gray-100',
          description: '工作流执行被用户取消'
        }
      default:
        return {
          icon: Clock,
          label: '未知状态',
          color: 'text-gray-600',
          bgColor: 'bg-gray-100',
          description: '未知的执行状态'
        }
    }
  }

  const handleCancel = () => {
    if (execution?.id) {
      cancelExecutionMutation.mutate(execution.id)
    }
  }

  const handleCopyResult = () => {
    if (execution?.result_data) {
      navigator.clipboard.writeText(JSON.stringify(execution.result_data, null, 2))
    }
  }

  const calculateProgress = () => {
    if (!execution || execution.total_nodes === 0) return 0
    return (execution.completed_nodes / execution.total_nodes) * 100
  }

  const calculateDuration = () => {
    if (!execution?.started_at) return null
    
    const endTime = execution.completed_at 
      ? new Date(execution.completed_at) 
      : new Date()
    const startTime = new Date(execution.started_at)
    
    const durationMs = endTime.getTime() - startTime.getTime()
    const durationSeconds = Math.floor(durationMs / 1000)
    
    if (durationSeconds < 60) {
      return `${durationSeconds} 秒`
    } else if (durationSeconds < 3600) {
      const minutes = Math.floor(durationSeconds / 60)
      const seconds = durationSeconds % 60
      return `${minutes} 分 ${seconds} 秒`
    } else {
      const hours = Math.floor(durationSeconds / 3600)
      const minutes = Math.floor((durationSeconds % 3600) / 60)
      return `${hours} 小时 ${minutes} 分`
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
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
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <DialogTitle className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <FileText className="w-4 h-4 text-white" />
              </div>
              执行详情 #{executionId}
            </DialogTitle>
            <DialogDescription>
              查看工作流执行的详细信息和结果
            </DialogDescription>
          </motion.div>
        </DialogHeader>

        <div className="flex-1 overflow-hidden">
          {isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-24 w-full" />
            </div>
          ) : execution ? (
            <ScrollArea className="h-full pr-4">
              <motion.div
                variants={itemVariants}
                initial="hidden"
                animate="visible"
                className="space-y-6"
              >
                {/* 状态概览 */}
                <div className="bg-muted/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      {(() => {
                        const statusConfig = getStatusConfig(execution.status)
                        const StatusIcon = statusConfig.icon
                        return (
                          <>
                            <StatusIcon className={cn("w-5 h-5", statusConfig.color)} />
                            <div>
                              <Badge className={cn(statusConfig.bgColor, statusConfig.color)}>
                                {statusConfig.label}
                              </Badge>
                              <p className="text-sm text-muted-foreground mt-1">
                                {statusConfig.description}
                              </p>
                            </div>
                          </>
                        )
                      })()}
                    </div>
                    
                    {execution.status === ExecutionStatus.RUNNING && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleCancel}
                        disabled={cancelExecutionMutation.isPending}
                        className="gap-2"
                      >
                        <Pause className="w-4 h-4" />
                        {cancelExecutionMutation.isPending ? '取消中...' : '取消执行'}
                      </Button>
                    )}
                  </div>

                  {/* 进度信息 */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">执行进度</span>
                      <span className="font-medium">
                        {execution.completed_nodes}/{execution.total_nodes} 
                        ({Math.round(calculateProgress())}%)
                      </span>
                    </div>
                    <Progress value={calculateProgress()} className="h-2" />
                    
                    {execution.failed_nodes > 0 && (
                      <div className="flex items-center gap-2 text-sm text-red-600">
                        <AlertTriangle className="w-4 h-4" />
                        <span>{execution.failed_nodes} 个节点执行失败</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* 时间信息 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h3 className="font-medium text-foreground flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      时间信息
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">创建时间:</span>
                        <span>{format(new Date(execution.created_at), 'yyyy-MM-dd HH:mm:ss')}</span>
                      </div>
                      {execution.started_at && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">开始时间:</span>
                          <span>{format(new Date(execution.started_at), 'yyyy-MM-dd HH:mm:ss')}</span>
                        </div>
                      )}
                      {execution.completed_at && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">完成时间:</span>
                          <span>{format(new Date(execution.completed_at), 'yyyy-MM-dd HH:mm:ss')}</span>
                        </div>
                      )}
                      {calculateDuration() && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">执行时长:</span>
                          <span className="font-medium">{calculateDuration()}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <h3 className="font-medium text-foreground flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      执行统计
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">总节点数:</span>
                        <span>{execution.total_nodes}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">已完成:</span>
                        <span className="text-green-600">{execution.completed_nodes}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">失败数:</span>
                        <span className="text-red-600">{execution.failed_nodes}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* 错误信息 */}
                {execution.error_message && (
                  <div className="space-y-2">
                    <h3 className="font-medium text-foreground flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-500" />
                      错误信息
                    </h3>
                    <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
                      <p className="text-sm text-red-700 dark:text-red-300 font-mono">
                        {execution.error_message}
                      </p>
                    </div>
                  </div>
                )}

                {/* 执行结果 */}
                {execution.result_data && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium text-foreground flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        执行结果
                      </h3>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleCopyResult}
                          className="gap-2"
                        >
                          <Copy className="w-3 h-3" />
                          复制
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="gap-2"
                        >
                          <Download className="w-3 h-3" />
                          下载
                        </Button>
                      </div>
                    </div>
                    <div className="bg-muted/50 rounded-lg p-3 max-h-64 overflow-auto">
                      <pre className="text-xs text-foreground font-mono whitespace-pre-wrap">
                        {JSON.stringify(execution.result_data, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </motion.div>
            </ScrollArea>
          ) : (
            <div className="flex items-center justify-center h-32">
              <p className="text-muted-foreground">加载执行详情失败</p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}