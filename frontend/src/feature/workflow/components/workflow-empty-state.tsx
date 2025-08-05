import { motion } from 'framer-motion'
import { ArrowRight, Plus, Sparkles, Workflow } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

interface WorkflowEmptyStateProps {
  onCreateWorkflow?: () => void
}

export function WorkflowEmptyState({ onCreateWorkflow }: WorkflowEmptyStateProps) {
  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: 'easeOut',
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.4,
        ease: 'easeOut'
      }
    }
  }

  const floatingVariants = {
    animate: {
      y: [-10, 10, -10],
      rotate: [0, 5, -5, 0],
      transition: {
        duration: 6,
        repeat: Infinity,
        ease: 'easeInOut'
      }
    }
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="flex flex-col items-center justify-center min-h-[600px] p-8"
    >
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          variants={floatingVariants}
          animate="animate"
          className="absolute top-20 left-20 w-32 h-32 bg-gradient-to-br from-blue-400/10 to-purple-400/10 rounded-full blur-xl"
        />
        <motion.div
          variants={floatingVariants}
          animate="animate"
          style={{ animationDelay: '2s' }}
          className="absolute bottom-20 right-20 w-24 h-24 bg-gradient-to-br from-green-400/10 to-blue-400/10 rounded-full blur-xl"
        />
        <motion.div
          variants={floatingVariants}
          animate="animate"
          style={{ animationDelay: '4s' }}
          className="absolute top-1/2 right-1/4 w-16 h-16 bg-gradient-to-br from-purple-400/10 to-pink-400/10 rounded-full blur-lg"
        />
      </div>

      {/* 主要内容 */}
      <motion.div variants={itemVariants} className="relative z-10">
        <Card className="border-dashed border-2 border-border/50 bg-card/50 backdrop-blur-sm">
          <CardContent className="flex flex-col items-center text-center p-12 max-w-md">
            {/* 图标区域 */}
            <motion.div
              variants={itemVariants}
              className="relative mb-6"
            >
              <div className="relative">
                <motion.div
                  animate={{
                    scale: [1, 1.1, 1],
                    rotate: [0, 10, -10, 0]
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: 'easeInOut'
                  }}
                  className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg"
                >
                  <Workflow className="w-10 h-10 text-white" />
                </motion.div>

                {/* 装饰性图标 */}
                <motion.div
                  animate={{
                    y: [-5, 5, -5],
                    opacity: [0.5, 1, 0.5]
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: 'easeInOut'
                  }}
                  className="absolute -top-2 -right-2 w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center"
                >
                  <Sparkles className="w-3 h-3 text-white" />
                </motion.div>
              </div>
            </motion.div>

            {/* 文字内容 */}
            <motion.div variants={itemVariants} className="space-y-4">
              <h2 className="text-2xl font-bold text-foreground">
                开始创建您的第一个工作流
              </h2>
              <p className="text-muted-foreground leading-relaxed">
                工作流可以帮助您自动化复杂的任务流程。通过可视化的节点编辑器，
                您可以轻松构建强大的自动化解决方案。
              </p>
            </motion.div>

            {/* 功能特点 */}
            <motion.div variants={itemVariants} className="grid grid-cols-1 gap-3 mt-6 w-full">
              {[
                { icon: Workflow, text: '可视化流程设计' },
                { icon: Sparkles, text: 'AI 驱动的智能节点' },
                { icon: ArrowRight, text: '实时执行监控' }
              ].map((feature, _index) => (
                <motion.div
                  key={feature.text}
                  variants={itemVariants}
                  className="flex items-center gap-3 p-3 rounded-lg bg-muted/50"
                >
                  <feature.icon className="w-4 h-4 text-primary" />
                  <span className="text-sm text-foreground">{feature.text}</span>
                </motion.div>
              ))}
            </motion.div>

            {/* 创建按钮 */}
            <motion.div
              variants={itemVariants}
              className="mt-8"
            >
              <Button
                onClick={onCreateWorkflow}
                size="lg"
                className="gap-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <Plus className="w-5 h-5" />
                创建工作流
              </Button>
            </motion.div>

            {/* 提示文字 */}
            <motion.p
              variants={itemVariants}
              className="text-xs text-muted-foreground mt-4"
            >
              或者从模板开始，快速上手
            </motion.p>
          </CardContent>
        </Card>
      </motion.div>

      {/* 底部装饰线条 */}
      <motion.div
        variants={itemVariants}
        className="mt-12 w-full max-w-2xl"
      >
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-border/30" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-4 text-muted-foreground">现代化工作流管理</span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}