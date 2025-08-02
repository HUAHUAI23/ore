import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion } from 'framer-motion'
import { Loader2, Sparkles, Workflow } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { NodeType } from '@/types/workflow'
import { type QuickWorkflowCreateFormValues, quickWorkflowCreateSchema } from '@/validation/workflow'

import { useCreateWorkflow } from '../hooks'

interface CreateWorkflowDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function CreateWorkflowDialog({ open, onOpenChange }: CreateWorkflowDialogProps) {
  const createWorkflowMutation = useCreateWorkflow()

  const form = useForm<QuickWorkflowCreateFormValues>({
    resolver: zodResolver(quickWorkflowCreateSchema),
    defaultValues: {
      name: '',
      description: '',
    },
  })

  const onSubmit = (data: QuickWorkflowCreateFormValues) => {
    // 创建基础工作流结构
    const workflowData = {
      ...data,
      version: '1.0.0',
      type: 'tree',
      nodes: {
        start: {
          id: 'start',
          name: '开始',
          description: '工作流开始节点',
          prompt: '',
          node_type: NodeType.START,
          input_config: {
            include_prompt: true,
            include_previous_output: true,
          },
        },
      },
      edges: [],
    }

    createWorkflowMutation.mutate(workflowData, {
      onSuccess: () => {
        onOpenChange(false)
        form.reset()
      },
    })
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3,
        ease: 'easeOut'
      }
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="flex items-center gap-3 mb-2"
          >
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Workflow className="w-5 h-5 text-white" />
            </div>
            <div>
              <DialogTitle className="text-left">创建新工作流</DialogTitle>
              <DialogDescription className="text-left">
                填写基本信息来创建您的工作流
              </DialogDescription>
            </div>
          </motion.div>
        </DialogHeader>

        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <motion.div
            variants={itemVariants}
            initial="hidden"
            animate="visible"
            className="space-y-2"
          >
            <Label htmlFor="name">工作流名称</Label>
            <Input
              id="name"
              placeholder="输入工作流名称..."
              {...form.register('name')}
              aria-invalid={!!form.formState.errors.name}
            />
            {form.formState.errors.name && (
              <p className="text-sm text-destructive">
                {form.formState.errors.name.message}
              </p>
            )}
          </motion.div>

          <motion.div
            variants={itemVariants}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.1 }}
            className="space-y-2"
          >
            <Label htmlFor="description">描述</Label>
            <Textarea
              id="description"
              placeholder="描述这个工作流的用途..."
              rows={3}
              {...form.register('description')}
              aria-invalid={!!form.formState.errors.description}
            />
            {form.formState.errors.description && (
              <p className="text-sm text-destructive">
                {form.formState.errors.description.message}
              </p>
            )}
          </motion.div>

          {/* 模板选择提示 */}
          <motion.div
            variants={itemVariants}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.2 }}
            className="p-3 bg-muted/50 rounded-lg border border-dashed border-border"
          >
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Sparkles className="w-4 h-4" />
              <span>创建后可以在编辑器中添加更多节点和配置</span>
            </div>
          </motion.div>

          <motion.div
            variants={itemVariants}
            initial="hidden"
            animate="visible"
            transition={{ delay: 0.3 }}
            className="flex justify-end gap-3 pt-4"
          >
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={createWorkflowMutation.isPending}
            >
              取消
            </Button>
            <Button
              type="submit"
              disabled={createWorkflowMutation.isPending}
              className="gap-2"
            >
              {createWorkflowMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  创建中...
                </>
              ) : (
                <>
                  <Workflow className="w-4 h-4" />
                  创建工作流
                </>
              )}
            </Button>
          </motion.div>
        </form>
      </DialogContent>
    </Dialog>
  )
}