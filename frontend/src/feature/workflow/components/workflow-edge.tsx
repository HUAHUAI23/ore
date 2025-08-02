import { memo } from 'react'
import {
  BaseEdge,
  EdgeLabelRenderer,
  type EdgeProps,
  getBezierPath,
  useReactFlow
} from '@xyflow/react'
import { motion } from 'framer-motion'
import { X } from 'lucide-react'

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
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'all',
          }}
          className="nodrag nopan"
        >
          {/* 条件标签 */}
          {hasCondition && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.2 }}
              className="mb-2"
            >
              <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-800">
                {edgeData?.condition?.match_type}: {edgeData?.condition?.match_value}
              </Badge>
            </motion.div>
          )}
          
          {/* 删除按钮 - 始终在边的中间显示 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.2 }}
            className="flex justify-center"
          >
            <Button
              variant="destructive"
              size="sm"
              className="h-6 w-6 p-0 rounded-full bg-red-500 hover:bg-red-600 text-white shadow-md"
              onClick={(e) => {
                e.stopPropagation()
                onEdgeClick()
              }}
              title="删除连接线"
            >
              <X className="h-3 w-3" />
            </Button>
          </motion.div>
        </div>
      </EdgeLabelRenderer>
    </>
  )
})

WorkflowEdge.displayName = 'WorkflowEdge'