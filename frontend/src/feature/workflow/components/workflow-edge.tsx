import { memo, useState } from 'react'
import {
  BaseEdge,
  EdgeLabelRenderer,
  type EdgeProps,
  getBezierPath,
  useReactFlow
} from '@xyflow/react'
import { X } from 'lucide-react'

import { Badge } from '@/components/ui/badge'

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
  selected,
}: EdgeProps) => {
  const { setEdges } = useReactFlow()
  const [isHovered, setIsHovered] = useState(false)

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
      {/* 连接线 */}
      <g
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        style={{ cursor: 'pointer' }}
      >
        <BaseEdge
          path={edgePath}
          markerEnd={markerEnd}
          style={{
            ...(style || {}),
            strokeWidth: selected || isHovered ? 3 : 2,
            stroke: hasCondition ? '#3b82f6' : (selected || isHovered ? '#374151' : '#6b7280'),
          }}
        />
        {/* 透明的宽边，便于鼠标交互 */}
        <path
          d={edgePath}
          fill="none"
          stroke="transparent"
          strokeWidth="20"
          style={{ cursor: 'pointer' }}
        />
      </g>

      {/* 删除按钮 - 悬停或选中时显示 */}
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'all',
            opacity: (isHovered || selected) ? 1 : 0,
            transition: 'opacity 0.2s ease-in-out',
          }}
          className="nodrag nopan"
        >
          <button
            className="w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center shadow-lg transition-all duration-200 hover:scale-110"
            onClick={(e) => {
              e.stopPropagation()
              onEdgeClick()
            }}
            title="删除连接线"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      </EdgeLabelRenderer>

      {/* 条件标签 - 仅在有条件时显示 */}
      {hasCondition && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -120%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: 'all',
            }}
            className="nodrag nopan"
          >
            <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-800 shadow-sm">
              {edgeData?.condition?.match_type}: {edgeData?.condition?.match_value}
            </Badge>
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  )
})

WorkflowEdge.displayName = 'WorkflowEdge'