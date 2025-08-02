import { memo } from 'react'
import { Handle, type NodeProps, Position } from '@xyflow/react'
import { motion } from 'framer-motion'
import {
  Play,
  Settings,
  Target,
  Workflow,
  Zap
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import type { ConditionConfig } from '@/types/workflow'
import { NodeType } from '@/types/workflow'

interface WorkflowNodeData {
  label: string
  description: string
  prompt: string
  nodeType: NodeType
  conditions?: ConditionConfig[]
}

interface WorkflowNodeProps extends NodeProps {
  data: WorkflowNodeData
  onEdit?: (nodeId: string, nodeData: WorkflowNodeData) => void
}

export const WorkflowNode = memo(({ id, data, selected, ...props }: WorkflowNodeProps) => {

  const getNodeConfig = (nodeType: NodeType) => {
    switch (nodeType) {
      case NodeType.START:
        return {
          icon: Play,
          color: 'from-green-500 to-emerald-600',
          bgColor: 'bg-green-50 dark:bg-green-950/20',
          borderColor: 'border-green-200 dark:border-green-800',
          badge: { label: '开始', variant: 'default' as const, className: 'bg-green-100 text-green-800' }
        }
      case NodeType.INTERMEDIATE:
        return {
          icon: Workflow,
          color: 'from-blue-500 to-blue-600',
          bgColor: 'bg-blue-50 dark:bg-blue-950/20',
          borderColor: 'border-blue-200 dark:border-blue-800',
          badge: { label: '处理', variant: 'secondary' as const, className: 'bg-blue-100 text-blue-800' }
        }
      case NodeType.LEAF:
        return {
          icon: Target,
          color: 'from-amber-500 to-orange-600',
          bgColor: 'bg-amber-50 dark:bg-amber-950/20',
          borderColor: 'border-amber-200 dark:border-amber-800',
          badge: { label: '结束', variant: 'outline' as const, className: 'bg-amber-100 text-amber-800' }
        }
      default:
        return {
          icon: Zap,
          color: 'from-gray-500 to-gray-600',
          bgColor: 'bg-gray-50 dark:bg-gray-950/20',
          borderColor: 'border-gray-200 dark:border-gray-800',
          badge: { label: '未知', variant: 'secondary' as const, className: 'bg-gray-100 text-gray-800' }
        }
    }
  }

  const config = getNodeConfig(data.nodeType)
  const IconComponent = config.icon

  const handleEdit = () => {
    props.onEdit?.(id, data)
  }

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
      className="relative"
    >
      <Card
        className={cn(
          "w-64 shadow-lg transition-all duration-200 group",
          config.bgColor,
          config.borderColor,
          selected ? "ring-2 ring-primary ring-offset-2" : "hover:shadow-xl"
        )}
      >
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={cn(
                "w-8 h-8 rounded-lg bg-gradient-to-br flex items-center justify-center",
                config.color
              )}>
                <IconComponent className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-sm text-foreground truncate">
                  {data.label}
                </h3>
              </div>
            </div>
            <Badge
              variant={config.badge.variant}
              className={cn("text-xs", config.badge.className)}
            >
              {config.badge.label}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="pt-0">
          <p className="text-xs text-muted-foreground line-clamp-2 mb-3">
            {data.description}
          </p>

          {data.prompt && (
            <div className="mb-3">
              <div className="text-xs font-medium text-foreground mb-1">提示词</div>
              <div className="text-xs text-muted-foreground bg-muted/50 rounded px-2 py-1 line-clamp-2">
                {data.prompt}
              </div>
            </div>
          )}

          {data.conditions && data.conditions.length > 0 && (
            <div className="mb-3">
              <div className="text-xs font-medium text-foreground mb-1">输出条件</div>
              <div className="flex flex-wrap gap-1">
                {data.conditions.map((condition: ConditionConfig, index: number) => (
                  <Badge
                    key={index}
                    variant="outline"
                    className="text-xs px-1 py-0 bg-blue-50 border-blue-200"
                    title={`连接点: condition-${index}`}
                  >
                    <span className="text-blue-600 font-mono mr-1">{index}</span>
                    {condition.match_type}:{condition.match_value}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={handleEdit}
            >
              <Settings className="w-3 h-3 mr-1" />
              配置
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 连接点 */}
      {data.nodeType !== NodeType.START && (
        <Handle
          type="target"
          position={Position.Left}
          className="w-3 h-3 bg-border border-2 border-background"
        />
      )}

      {data.nodeType !== NodeType.LEAF && (
        <>
          {/* 条件连接点和默认连接点 */}
          {data.conditions && data.conditions.length > 0 ? (
            // 有条件时：为每个条件创建连接点
            data.conditions.map((condition: ConditionConfig, index: number) => {
              const totalConditions = data.conditions!.length
              // 改进位置计算：从20%开始，到80%结束，均匀分布
              const topPosition = totalConditions === 1
                ? 50 // 单个条件时居中
                : 20 + (index * 60) / (totalConditions - 1) // 多个条件时均匀分布

              return (
                <Handle
                  key={`${id}-condition-${index}-${condition.match_type}-${condition.match_value}`}
                  type="source"
                  position={Position.Right}
                  id={`condition-${index}`}
                  className="w-4 h-4 bg-blue-500 border-2 border-white shadow-lg hover:bg-blue-600 hover:scale-110 transition-all duration-200 cursor-pointer"
                  style={{
                    top: `${topPosition}%`,
                    right: '-8px',
                    zIndex: 10 + index,
                    position: 'absolute'
                  }}
                  title={`条件 [${index}]: ${condition.match_type} "${condition.match_value}"`}
                />
              )
            })
          ) : (
            // 无条件时：显示默认连接点
            <Handle
              type="source"
              position={Position.Right}
              id="default"
              className="w-3 h-3 bg-border border-2 border-background hover:bg-gray-400 transition-colors"
              style={{ top: '50%', zIndex: 5 }}
              title="默认连接点"
            />
          )}
        </>
      )}
    </motion.div>
  )
})

WorkflowNode.displayName = 'WorkflowNode'