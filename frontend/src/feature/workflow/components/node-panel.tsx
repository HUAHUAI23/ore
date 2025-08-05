import { motion } from 'framer-motion'
import {
    GripVertical,
    Play,
    Target,
    Workflow,
    X
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { NodeType } from '@/types/workflow'

interface NodePanelProps {
    className?: string
    onAddNode: (nodeType: NodeType) => void
    onClose?: () => void
}

export function NodePanel({ className, onAddNode, onClose }: NodePanelProps) {
    const nodeTypes = [
        {
            type: NodeType.START,
            label: '开始节点',
            description: '工作流的起始点',
            icon: Play,
            color: 'from-green-500 to-emerald-600',
            bgColor: 'bg-green-50 hover:bg-green-100',
            textColor: 'text-green-700',
        },
        {
            type: NodeType.INTERMEDIATE,
            label: '处理节点',
            description: '执行具体的处理逻辑',
            icon: Workflow,
            color: 'from-blue-500 to-blue-600',
            bgColor: 'bg-blue-50 hover:bg-blue-100',
            textColor: 'text-blue-700',
        },
        {
            type: NodeType.LEAF,
            label: '结束节点',
            description: '工作流的终点',
            icon: Target,
            color: 'from-amber-500 to-orange-600',
            bgColor: 'bg-amber-50 hover:bg-amber-100',
            textColor: 'text-amber-700',
        },
    ]

    const handleDragStart = (event: React.DragEvent, nodeType: NodeType) => {
        event.dataTransfer.setData('application/reactflow', nodeType)
        event.dataTransfer.effectAllowed = 'move'
    }

    return (
        <motion.div
            initial={{ x: -300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className={cn(
                "absolute top-0 left-0 z-20 w-72 h-full bg-background/95 backdrop-blur-sm border-r border-border overflow-y-auto shadow-2xl",
                className
            )}
        >
            <Card className="m-4 shadow-sm">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">节点面板</CardTitle>
                    {onClose && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={onClose}
                            className="h-8 w-8 p-0"
                        >
                            <X className="h-4 w-4" />
                        </Button>
                    )}
                </CardHeader>
                <CardContent className="space-y-2">
                    {nodeTypes.map((nodeType, index) => {
                        const IconComponent = nodeType.icon
                        return (
                            <motion.div
                                key={nodeType.type}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                            >
                                <Button
                                    variant="ghost"
                                    className={cn(
                                        "w-full justify-start h-auto p-3 cursor-grab active:cursor-grabbing",
                                        nodeType.bgColor,
                                        nodeType.textColor
                                    )}
                                    draggable
                                    onDragStart={(e) => handleDragStart(e, nodeType.type)}
                                    onClick={() => onAddNode(nodeType.type)}
                                >
                                    <div className="flex items-center gap-3 w-full">
                                        <div className={cn(
                                            "w-8 h-8 rounded-lg bg-gradient-to-br flex items-center justify-center flex-shrink-0",
                                            nodeType.color
                                        )}>
                                            <IconComponent className="w-4 h-4 text-white" />
                                        </div>
                                        <div className="flex-1 text-left">
                                            <div className="font-medium text-sm">{nodeType.label}</div>
                                            <div className="text-xs opacity-70">{nodeType.description}</div>
                                        </div>
                                        <GripVertical className="w-4 h-4 opacity-40" />
                                    </div>
                                </Button>
                            </motion.div>
                        )
                    })}
                </CardContent>
            </Card>

            <Separator className="mx-4" />

            <div className="p-4">
                <div className="text-xs text-muted-foreground space-y-1">
                    <p>• 点击按钮添加节点到画布中心</p>
                    <p>• 拖拽按钮到画布指定位置</p>
                    <p>• 连接节点创建工作流</p>
                </div>
            </div>
        </motion.div>
    )
}