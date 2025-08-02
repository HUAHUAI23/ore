import { useEffect, useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion } from 'framer-motion'
import {
  Play,
  Plus,
  Settings,
  Target,
  Trash2,
  Workflow,
  X
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { cn } from '@/lib/utils'
import { NodeType } from '@/types/workflow'
import { type TreeNodeConfigFormValues, treeNodeConfigSchema } from '@/validation/workflow'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'

interface NodeEditDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  nodeData?: {
    id: string
    label: string
    description: string
    prompt: string
    nodeType: NodeType
    conditions?: Array<{
      match_target: string
      match_type: string
      match_value: string
      case_sensitive: boolean
    }>
  }
  onSave: (data: TreeNodeConfigFormValues) => void
}

export function NodeEditDialog({
  open,
  onOpenChange,
  nodeData,
  onSave
}: NodeEditDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<TreeNodeConfigFormValues>({
    resolver: zodResolver(treeNodeConfigSchema),
    defaultValues: {
      id: '',
      name: '',
      description: '',
      prompt: '',
      node_type: NodeType.INTERMEDIATE,
      conditions: [],
    },
  })

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'conditions'
  })

  // 当nodeData变化时更新表单
  useEffect(() => {
    if (nodeData) {
      form.reset({
        id: nodeData.id,
        name: nodeData.label,
        description: nodeData.description,
        prompt: nodeData.prompt,
        node_type: nodeData.nodeType,
        conditions: nodeData.conditions || [],
      })
    }
  }, [nodeData, form])

  const onSubmit = async (data: TreeNodeConfigFormValues) => {
    setIsSubmitting(true)
    try {
      await onSave(data)
      onOpenChange(false)
    } catch (error) {
      console.error('保存节点失败:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const getNodeTypeConfig = (nodeType: NodeType) => {
    switch (nodeType) {
      case NodeType.START:
        return {
          icon: Play,
          label: '开始节点',
          color: 'bg-green-100 text-green-800',
          description: '工作流的起始点，通常不需要提示词'
        }
      case NodeType.INTERMEDIATE:
        return {
          icon: Workflow,
          label: '处理节点',
          color: 'bg-blue-100 text-blue-800',
          description: '执行具体的处理逻辑，需要配置提示词'
        }
      case NodeType.LEAF:
        return {
          icon: Target,
          label: '结束节点',
          color: 'bg-amber-100 text-amber-800',
          description: '工作流的终点，可以配置总结性的提示词'
        }
      default:
        return {
          icon: Settings,
          label: '未知节点',
          color: 'bg-gray-100 text-gray-800',
          description: ''
        }
    }
  }

  const currentNodeType = form.watch('node_type')
  const nodeTypeConfig = getNodeTypeConfig(currentNodeType)
  const IconComponent = nodeTypeConfig.icon

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            节点配置
          </DialogTitle>
          <DialogDescription>
            配置节点的基本信息和处理逻辑
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              {/* 节点类型显示 */}
              <div className="flex items-center gap-3 p-3 rounded-lg border bg-muted/30">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                  <IconComponent className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{nodeTypeConfig.label}</span>
                    <Badge className={nodeTypeConfig.color}>
                      {currentNodeType}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {nodeTypeConfig.description}
                  </p>
                </div>
              </div>

              {/* 节点类型选择 */}
              <FormField
                control={form.control}
                name="node_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>节点类型</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="选择节点类型" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value={NodeType.START}>
                          <div className="flex items-center gap-2">
                            <Play className="w-4 h-4" />
                            开始节点
                          </div>
                        </SelectItem>
                        <SelectItem value={NodeType.INTERMEDIATE}>
                          <div className="flex items-center gap-2">
                            <Workflow className="w-4 h-4" />
                            处理节点
                          </div>
                        </SelectItem>
                        <SelectItem value={NodeType.LEAF}>
                          <div className="flex items-center gap-2">
                            <Target className="w-4 h-4" />
                            结束节点
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* 节点ID */}
              <FormField
                control={form.control}
                name="id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>节点ID</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="节点的唯一标识符" disabled />
                    </FormControl>
                    <FormDescription>
                      节点的唯一标识符，创建后不可修改
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* 节点名称 */}
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>节点名称</FormLabel>
                    <FormControl>
                      <Input {...field} placeholder="输入节点名称" />
                    </FormControl>
                    <FormDescription>
                      节点的显示名称，用于在画布上标识节点
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* 节点描述 */}
              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>节点描述</FormLabel>
                    <FormControl>
                      <Textarea
                        {...field}
                        placeholder="输入节点的详细描述"
                        className="min-h-[80px]"
                      />
                    </FormControl>
                    <FormDescription>
                      详细描述节点的功能和用途
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* 提示词 */}
              <FormField
                control={form.control}
                name="prompt"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      提示词
                      {currentNodeType === NodeType.START && (
                        <span className="text-muted-foreground text-sm ml-2">(可选)</span>
                      )}
                    </FormLabel>
                    <FormControl>
                      <Textarea
                        {...field}
                        placeholder={
                          currentNodeType === NodeType.START
                            ? "开始节点通常不需要提示词..."
                            : currentNodeType === NodeType.LEAF
                              ? "输入总结性的提示词..."
                              : "输入处理逻辑的提示词..."
                        }
                        className="min-h-[120px]"
                      />
                    </FormControl>
                    <FormDescription>
                      {currentNodeType === NodeType.START
                        ? "开始节点通常不需要提示词，除非需要初始化上下文"
                        : currentNodeType === NodeType.LEAF
                          ? "结束节点可以配置总结性的提示词"
                          : "配置节点执行时使用的AI提示词"
                      }
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* 条件配置 */}
              {(currentNodeType === NodeType.INTERMEDIATE || currentNodeType === NodeType.START) && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="space-y-4"
                >
                  <div className="flex items-center justify-between">
                    <Label className="text-base font-medium">输出条件</Label>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => append({
                        match_target: 'node_output',
                        match_type: 'contains' as const,
                        match_value: '',
                        case_sensitive: false
                      })}
                      className="gap-2"
                    >
                      <Plus className="h-4 w-4" />
                      添加条件
                    </Button>
                  </div>
                  
                  {fields.length === 0 && (
                    <p className="text-sm text-muted-foreground">
                      暂无条件配置，每个条件将生成一个连接点
                    </p>
                  )}
                  
                  {fields.map((field, index) => (
                    <motion.div
                      key={field.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="p-4 border rounded-lg space-y-3 bg-muted/30"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">条件 {index + 1}</span>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => remove(index)}
                          className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      {/* 隐藏的 match_target 字段 */}
                      <FormField
                        control={form.control}
                        name={`conditions.${index}.match_target`}
                        render={({ field }) => (
                          <FormItem className="hidden">
                            <FormControl>
                              <Input {...field} value="node_output" readOnly />
                            </FormControl>
                          </FormItem>
                        )}
                      />
                      
                      <div className="grid grid-cols-2 gap-3">
                        <FormField
                          control={form.control}
                          name={`conditions.${index}.match_type`}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>匹配方式</FormLabel>
                              <Select onValueChange={field.onChange} defaultValue={field.value}>
                                <FormControl>
                                  <SelectTrigger>
                                    <SelectValue placeholder="选择匹配方式" />
                                  </SelectTrigger>
                                </FormControl>
                                <SelectContent>
                                  <SelectItem value="contains">包含</SelectItem>
                                  <SelectItem value="not_contains">不包含</SelectItem>
                                  <SelectItem value="fuzzy">模糊匹配</SelectItem>
                                  <SelectItem value="regex">正则表达式</SelectItem>
                                </SelectContent>
                              </Select>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                        
                        <FormField
                          control={form.control}
                          name={`conditions.${index}.match_value`}
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel>匹配值</FormLabel>
                              <FormControl>
                                <Input {...field} placeholder="输入匹配值" />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>
                      
                      <FormField
                        control={form.control}
                        name={`conditions.${index}.case_sensitive`}
                        render={({ field }) => (
                          <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                            <FormControl>
                              <Checkbox
                                checked={field.value}
                                onCheckedChange={field.onChange}
                              />
                            </FormControl>
                            <div className="space-y-1 leading-none">
                              <FormLabel>区分大小写</FormLabel>
                              <FormDescription>
                                开启后将严格区分大小写字母
                              </FormDescription>
                            </div>
                          </FormItem>
                        )}
                      />
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </motion.div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isSubmitting}
              >
                取消
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? '保存中...' : '保存配置'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}