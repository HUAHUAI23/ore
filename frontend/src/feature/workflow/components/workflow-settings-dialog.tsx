import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion } from 'framer-motion'
import { 
  Settings, 
  Info,
  Zap,
  Users,
  Clock
} from 'lucide-react'

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
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { WorkflowStatus } from '@/types/workflow'
import { workflowUpdateSchema, type WorkflowUpdateFormValues } from '@/validation/workflow'

interface WorkflowSettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  workflowData?: {
    id: number
    name: string
    description: string
    version: string
    status: WorkflowStatus
    type: string
  }
  onSave: (data: WorkflowUpdateFormValues) => void
}

export function WorkflowSettingsDialog({ 
  open, 
  onOpenChange, 
  workflowData,
  onSave 
}: WorkflowSettingsDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<WorkflowUpdateFormValues>({
    resolver: zodResolver(workflowUpdateSchema),
    defaultValues: {
      name: '',
      description: '',
      version: '',
      status: WorkflowStatus.DRAFT,
    },
  })

  // 当workflowData变化时更新表单
  useEffect(() => {
    if (workflowData) {
      form.reset({
        name: workflowData.name,
        description: workflowData.description,
        version: workflowData.version,
        status: workflowData.status,
      })
    }
  }, [workflowData, form])

  const onSubmit = async (data: WorkflowUpdateFormValues) => {
    setIsSubmitting(true)
    try {
      await onSave(data)
      onOpenChange(false)
    } catch (error) {
      console.error('保存工作流设置失败:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const getStatusConfig = (status: WorkflowStatus) => {
    switch (status) {
      case WorkflowStatus.ACTIVE:
        return { 
          label: '活跃', 
          color: 'bg-green-100 text-green-800',
          description: '工作流正在运行中，可以执行'
        }
      case WorkflowStatus.INACTIVE:
        return { 
          label: '已停用', 
          color: 'bg-gray-100 text-gray-800',
          description: '工作流已停用，不能执行'
        }
      case WorkflowStatus.DRAFT:
        return { 
          label: '草稿', 
          color: 'bg-blue-100 text-blue-800',
          description: '工作流还在编辑中，未发布'
        }
      default:
        return { 
          label: '未知', 
          color: 'bg-gray-100 text-gray-800',
          description: ''
        }
    }
  }

  const currentStatus = form.watch('status')
  const statusConfig = getStatusConfig(currentStatus)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            工作流设置
          </DialogTitle>
          <DialogDescription>
            配置工作流的基本信息、执行参数和权限设置
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <Tabs defaultValue="basic" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="basic" className="flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  基本信息
                </TabsTrigger>
                <TabsTrigger value="execution" className="flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  执行配置
                </TabsTrigger>
                <TabsTrigger value="permissions" className="flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  权限设置
                </TabsTrigger>
              </TabsList>

              <TabsContent value="basic" className="space-y-4 mt-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-4"
                >
                  {/* 工作流名称 */}
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>工作流名称</FormLabel>
                        <FormControl>
                          <Input {...field} placeholder="输入工作流名称" />
                        </FormControl>
                        <FormDescription>
                          工作流的显示名称，用于标识和搜索
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* 工作流描述 */}
                  <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>工作流描述</FormLabel>
                        <FormControl>
                          <Textarea 
                            {...field} 
                            placeholder="输入工作流的详细描述"
                            className="min-h-[100px]"
                          />
                        </FormControl>
                        <FormDescription>
                          详细描述工作流的功能、用途和使用场景
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* 版本号 */}
                  <FormField
                    control={form.control}
                    name="version"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>版本号</FormLabel>
                        <FormControl>
                          <Input {...field} placeholder="例如: 1.0.0" />
                        </FormControl>
                        <FormDescription>
                          工作流的版本标识，建议使用语义化版本号
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* 状态配置 */}
                  <FormField
                    control={form.control}
                    name="status"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>工作流状态</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="选择工作流状态" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value={WorkflowStatus.DRAFT}>
                              <div className="flex items-center gap-2">
                                <Badge className="bg-blue-100 text-blue-800">草稿</Badge>
                                <span>编辑中，未发布</span>
                              </div>
                            </SelectItem>
                            <SelectItem value={WorkflowStatus.ACTIVE}>
                              <div className="flex items-center gap-2">
                                <Badge className="bg-green-100 text-green-800">活跃</Badge>
                                <span>正在运行，可执行</span>
                              </div>
                            </SelectItem>
                            <SelectItem value={WorkflowStatus.INACTIVE}>
                              <div className="flex items-center gap-2">
                                <Badge className="bg-gray-100 text-gray-800">已停用</Badge>
                                <span>已停用，不可执行</span>
                              </div>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                        <FormDescription>
                          {statusConfig.description}
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </motion.div>
              </TabsContent>

              <TabsContent value="execution" className="space-y-4 mt-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.1 }}
                  className="space-y-4"
                >
                  <div className="rounded-lg border p-4 bg-muted/30">
                    <div className="flex items-center gap-2 mb-3">
                      <Clock className="w-5 h-5" />
                      <h3 className="font-medium">执行配置</h3>
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">
                      配置工作流的执行参数和行为
                    </p>

                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <div className="text-sm font-medium">自动重试</div>
                          <div className="text-xs text-muted-foreground">
                            执行失败时自动重试
                          </div>
                        </div>
                        <Switch />
                      </div>

                      <Separator />

                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <div className="text-sm font-medium">并行执行</div>
                          <div className="text-xs text-muted-foreground">
                            允许节点并行执行以提高效率
                          </div>
                        </div>
                        <Switch />
                      </div>

                      <Separator />

                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <div className="text-sm font-medium">执行日志</div>
                          <div className="text-xs text-muted-foreground">
                            记录详细的执行日志
                          </div>
                        </div>
                        <Switch defaultChecked />
                      </div>
                    </div>
                  </div>

                </motion.div>
              </TabsContent>

              <TabsContent value="permissions" className="space-y-4 mt-6">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.2 }}
                  className="space-y-4"
                >
                  <div className="rounded-lg border p-4 bg-muted/30">
                    <div className="flex items-center gap-2 mb-3">
                      <Users className="w-5 h-5" />
                      <h3 className="font-medium">权限管理</h3>
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">
                      管理工作流的访问权限和操作权限
                    </p>

                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <div className="text-sm font-medium">公开访问</div>
                          <div className="text-xs text-muted-foreground">
                            允许其他用户查看此工作流
                          </div>
                        </div>
                        <Switch />
                      </div>

                      <Separator />

                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <div className="text-sm font-medium">允许复制</div>
                          <div className="text-xs text-muted-foreground">
                            允许其他用户复制此工作流
                          </div>
                        </div>
                        <Switch />
                      </div>

                      <Separator />

                      <div className="flex items-center justify-between">
                        <div className="space-y-0.5">
                          <div className="text-sm font-medium">协作编辑</div>
                          <div className="text-xs text-muted-foreground">
                            允许团队成员协作编辑
                          </div>
                        </div>
                        <Switch />
                      </div>
                    </div>
                  </div>
                </motion.div>
              </TabsContent>
            </Tabs>

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
                {isSubmitting ? '保存中...' : '保存设置'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}