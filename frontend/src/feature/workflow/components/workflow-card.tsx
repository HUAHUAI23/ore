import Tilt from 'react-parallax-tilt'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { motion } from 'framer-motion'
import {
  Calendar,
  CheckCircle,
  Clock,
  Edit,
  MoreVertical,
  Pause,
  Play,
  XCircle
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import type { WorkflowListItem } from '@/types/workflow'
import { WorkflowStatus } from '@/types/workflow'

interface WorkflowCardProps {
  workflow: WorkflowListItem
  onEdit?: (workflow: WorkflowListItem) => void
  onRun?: (workflow: WorkflowListItem) => void
  onDelete?: (workflow: WorkflowListItem) => void
  className?: string
}

export function WorkflowCard({
  workflow,
  onEdit,
  onRun,
  onDelete,
  className
}: WorkflowCardProps) {
  const getStatusConfig = (status: WorkflowStatus) => {
    switch (status) {
      case WorkflowStatus.ACTIVE:
        return {
          icon: CheckCircle,
          label: '活跃',
          variant: 'default' as const,
          className: 'bg-green-100 text-green-800 border-green-200'
        }
      case WorkflowStatus.INACTIVE:
        return {
          icon: Pause,
          label: '已停用',
          variant: 'secondary' as const,
          className: 'bg-gray-100 text-gray-800 border-gray-200'
        }
      case WorkflowStatus.DRAFT:
        return {
          icon: Edit,
          label: '草稿',
          variant: 'outline' as const,
          className: 'bg-blue-100 text-blue-800 border-blue-200'
        }
      case WorkflowStatus.DELETED:
        return {
          icon: XCircle,
          label: '已删除',
          variant: 'destructive' as const,
          className: 'bg-red-100 text-red-800 border-red-200'
        }
      default:
        return {
          icon: Clock,
          label: '未知',
          variant: 'secondary' as const,
          className: 'bg-gray-100 text-gray-800 border-gray-200'
        }
    }
  }

  const statusConfig = getStatusConfig(workflow.status)
  const StatusIcon = statusConfig.icon

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3,
        ease: 'easeOut'
      }
    },
    hover: {
      y: -5,
      transition: {
        duration: 0.2,
        ease: 'easeOut'
      }
    }
  }

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      className={className}
    >
      <Tilt
        tiltMaxAngleX={5}
        tiltMaxAngleY={5}
        perspective={1000}
        scale={1.02}
        transitionSpeed={400}
        gyroscope={true}
      >
        <Card className="h-full cursor-pointer group transition-all duration-200 hover:shadow-lg border-border/50 hover:border-border">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-lg text-foreground group-hover:text-primary transition-colors truncate">
                  {workflow.name}
                </h3>
                <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                  {workflow.description}
                </p>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => onEdit?.(workflow)}>
                    <Edit className="h-4 w-4 mr-2" />
                    编辑
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onRun?.(workflow)}>
                    <Play className="h-4 w-4 mr-2" />
                    运行
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => onDelete?.(workflow)}
                    className="text-destructive focus:text-destructive"
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    删除
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </CardHeader>

          <CardContent className="pt-0">
            <div className="space-y-4">
              {/* 状态和版本 */}
              <div className="flex items-center justify-between">
                <Badge
                  variant={statusConfig.variant}
                  className={cn("gap-1", statusConfig.className)}
                >
                  <StatusIcon className="h-3 w-3" />
                  {statusConfig.label}
                </Badge>
                <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                  v{workflow.version}
                </span>
              </div>

              {/* 元数据 */}
              <div className="space-y-2 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Calendar className="h-3 w-3" />
                  <span>类型: {workflow.type}</span>
                </div>
                {workflow.updated_at && (
                  <div className="flex items-center gap-2">
                    <Clock className="h-3 w-3" />
                    <span>
                      更新于 {formatDistanceToNow(new Date(workflow.updated_at), {
                        addSuffix: true,
                        locale: zhCN
                      })}
                    </span>
                  </div>
                )}
              </div>

              {/* 操作按钮 */}
              <div className="flex gap-2 pt-2">
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1 gap-2"
                  onClick={() => onEdit?.(workflow)}
                >
                  <Edit className="h-3 w-3" />
                  编辑
                </Button>
                <Button
                  size="sm"
                  className="flex-1 gap-2"
                  onClick={() => onRun?.(workflow)}
                  disabled={workflow.status !== WorkflowStatus.ACTIVE}
                >
                  <Play className="h-3 w-3" />
                  运行
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </Tilt>
    </motion.div>
  )
}