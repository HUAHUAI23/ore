import { useMemo } from 'react'
import { useReactFlow } from '@xyflow/react'
import { AnimatePresence,motion } from 'framer-motion'
import { Copy, Settings,Trash2 } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { useWorkflowEditorStore } from '@/stores/workflow-editor'

interface WorkflowSelectionToolbarProps {
  selectedNodes: string[]
  onDeleteNodes: (nodeIds: string[]) => void
  onEditNode?: (nodeId: string) => void
}

export function WorkflowSelectionToolbar({
  selectedNodes,
  onDeleteNodes,
  onEditNode
}: WorkflowSelectionToolbarProps) {
  const { getViewport } = useReactFlow()
  const { nodes } = useWorkflowEditorStore()
  
  const selectedNodeData = useMemo(() => {
    return selectedNodes.map(id => nodes.find(node => node.id === id)).filter(Boolean)
  }, [selectedNodes, nodes])

  const handleDelete = () => {
    onDeleteNodes(selectedNodes)
  }

  const handleCopy = () => {
    // TODO: 实现复制功能
    console.log('Copy nodes:', selectedNodes)
  }

  const handleEdit = () => {
    if (selectedNodes.length === 1 && onEditNode) {
      onEditNode(selectedNodes[0])
    }
  }

  if (selectedNodes.length === 0) {
    return null
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -20, scale: 0.95 }}
        transition={{ duration: 0.2 }}
        className="absolute top-4 left-1/2 transform -translate-x-1/2 z-50"
      >
        <Card className="bg-background/95 backdrop-blur-sm border border-border shadow-lg">
          <div className="flex items-center gap-2 px-4 py-2">
            {/* 选中节点信息 */}
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                {selectedNodes.length} 个节点
              </Badge>
              {selectedNodeData.length > 0 && (
                <span className="text-sm text-muted-foreground">
                  {selectedNodeData.map(node => node?.data?.label).join(', ')}
                </span>
              )}
            </div>

            <Separator orientation="vertical" className="h-6" />

            {/* 操作按钮 */}
            <div className="flex items-center gap-1">
              {/* 编辑按钮 - 仅单选时显示 */}
              {selectedNodes.length === 1 && onEditNode && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2"
                  onClick={handleEdit}
                  title="编辑节点"
                >
                  <Settings className="h-4 w-4" />
                </Button>
              )}

              {/* 复制按钮 */}
              <Button
                variant="ghost"
                size="sm"
                className="h-8 px-2"
                onClick={handleCopy}
                title="复制节点"
              >
                <Copy className="h-4 w-4" />
              </Button>

              {/* 删除按钮 */}
              <Button
                variant="ghost"
                size="sm"
                className="h-8 px-2 text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={handleDelete}
                title="删除节点"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>
      </motion.div>
    </AnimatePresence>
  )
}