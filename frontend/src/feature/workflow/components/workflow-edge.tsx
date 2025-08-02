import { memo } from 'react'
import {
  BaseEdge,
  EdgeLabelRenderer,
  type EdgeProps,
  getBezierPath,
  useReactFlow
} from '@xyflow/react'
import { motion } from 'framer-motion'
import { Settings, X } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

interface WorkflowEdgeData {
  condition?: {
    match_type: string
    match_value: string
  } | null
  inputConfig?: {
    include_prompt: boolean
    include_previous_output: boolean
  }
}

export const WorkflowEdge = memo(({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  data = {},
  markerEnd,
}: EdgeProps) => {
  const { setEdges } = useReactFlow()

  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  })

  const onEdgeClick = () => {
    setEdges((edges) => edges.filter((edge) => edge.id !== id))
  }

  const edgeData = data as WorkflowEdgeData | undefined
  const hasCondition = edgeData?.condition && edgeData.condition.match_value

  return (
    <>
      <BaseEdge
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...(style || {}),
          strokeWidth: 2,
          stroke: hasCondition ? '#3b82f6' : '#6b7280',
        }}
      />

      <EdgeLabelRenderer>
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2 }}
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            fontSize: 12,
            pointerEvents: 'all',
          }}
          className="nodrag nopan"
        >
          <div className="flex items-center gap-2 bg-background border border-border rounded-lg shadow-sm px-2 py-1">
            {hasCondition && (
              <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-800">
                {edgeData?.condition?.match_type}: {edgeData?.condition?.match_value}
              </Badge>
            )}

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                className="h-5 w-5 p-0 hover:bg-muted"
                onClick={(e) => {
                  e.stopPropagation()
                  // TODO: 打开边配置对话框
                }}
              >
                <Settings className="h-3 w-3" />
              </Button>

              <Button
                variant="ghost"
                size="sm"
                className="h-5 w-5 p-0 hover:bg-destructive hover:text-destructive-foreground"
                onClick={(e) => {
                  e.stopPropagation()
                  onEdgeClick()
                }}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </motion.div>
      </EdgeLabelRenderer>
    </>
  )
})

WorkflowEdge.displayName = 'WorkflowEdge'