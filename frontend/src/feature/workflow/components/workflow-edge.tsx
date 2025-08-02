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
      {/* 连接线主体 */}
      <BaseEdge
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...(style || {}),
          strokeWidth: selected || isHovered ? 3 : 2,
          stroke: hasCondition ? '#3b82f6' : (selected || isHovered ? '#374151' : '#6b7280'),
        }}
      />

      {/* 整体悬停区域 - 包含连接线和按钮 */}
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'all',
            width: '60px',
            height: '60px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          className="nodrag nopan"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <button
            className={`w-8 h-8 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center shadow-lg transition-all duration-200 hover:scale-110 ${
              (isHovered || selected) ? 'opacity-100 scale-100' : 'opacity-0 scale-75'
            }`}
            onClick={(e) => {
              e.stopPropagation()
              onEdgeClick()
            }}
            title="删除连接线"
            style={{
              transition: 'all 0.2s ease-in-out',
            }}
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </EdgeLabelRenderer>

      {/* 大范围透明悬停区域 */}
      <path
        d={edgePath}
        fill="none"
        stroke="transparent"
        strokeWidth="30"
        style={{ cursor: 'pointer' }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      />

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