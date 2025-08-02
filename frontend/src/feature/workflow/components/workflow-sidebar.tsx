import { motion } from 'framer-motion'
import {
  Filter,
  LogOut,
  Plus,
  Search,
  Settings,
  User,
  Workflow
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'

interface WorkflowSidebarProps {
  className?: string
}

export function WorkflowSidebar({ className }: WorkflowSidebarProps) {
  const sidebarVariants = {
    hidden: { x: -280, opacity: 0 },
    visible: {
      x: 0,
      opacity: 1,
      transition: {
        duration: 0.3,
        ease: 'easeOut'
      }
    }
  }

  const menuItems = [
    { icon: Workflow, label: '工作流', active: true },
    { icon: Settings, label: '设置', active: false },
  ]

  return (
    <motion.div
      variants={sidebarVariants}
      initial="hidden"
      animate="visible"
      className={cn(
        "fixed left-0 top-0 z-40 h-screen w-72 bg-sidebar border-r border-sidebar-border",
        "flex flex-col shadow-lg",
        className
      )}
    >
      {/* Logo区域 */}
      <div className="flex items-center gap-3 px-6 py-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sidebar-primary">
          <Workflow className="h-5 w-5 text-sidebar-primary-foreground" />
        </div>
        <span className="text-lg font-semibold text-sidebar-foreground">FlowAI</span>
      </div>

      <Separator className="bg-sidebar-border" />

      {/* 搜索区域 */}
      <div className="px-4 py-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-sidebar-foreground/60" />
          <Input
            placeholder="搜索工作流..."
            className="pl-9 bg-sidebar-accent border-sidebar-border text-sidebar-foreground placeholder:text-sidebar-foreground/60"
          />
        </div>
      </div>

      {/* 快速操作 */}
      <div className="px-4 pb-3">
        <Button
          className="w-full justify-start gap-2 bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary/90"
          size="sm"
        >
          <Plus className="h-4 w-4" />
          新建工作流
        </Button>
      </div>

      <Separator className="bg-sidebar-border" />

      {/* 导航菜单 */}
      <nav className="flex-1 px-4 py-2">
        <div className="space-y-1">
          {menuItems.map((item, index) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Button
                variant={item.active ? "default" : "ghost"}
                className={cn(
                  "w-full justify-start gap-3 h-10",
                  item.active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Button>
            </motion.div>
          ))}
        </div>

        {/* 过滤器 */}
        <div className="mt-6">
          <div className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-sidebar-foreground/80">
            <Filter className="h-4 w-4" />
            筛选
          </div>
          <div className="space-y-1 mt-2">
            {[
              { label: '全部', count: 12, active: true },
              { label: '活跃', count: 8, active: false },
              { label: '草稿', count: 3, active: false },
              { label: '已停用', count: 1, active: false },
            ].map((filter, index) => (
              <motion.div
                key={filter.label}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.05 }}
              >
                <Button
                  variant="ghost"
                  size="sm"
                  className={cn(
                    "w-full justify-between h-8 px-3",
                    filter.active
                      ? "bg-sidebar-accent/50 text-sidebar-accent-foreground"
                      : "text-sidebar-foreground/70 hover:bg-sidebar-accent/30 hover:text-sidebar-foreground"
                  )}
                >
                  <span>{filter.label}</span>
                  <span className="text-xs bg-sidebar-accent/30 px-1.5 py-0.5 rounded">
                    {filter.count}
                  </span>
                </Button>
              </motion.div>
            ))}
          </div>
        </div>
      </nav>

      <Separator className="bg-sidebar-border" />

      {/* 用户区域 */}
      <div className="p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-sidebar-accent">
            <User className="h-4 w-4 text-sidebar-accent-foreground" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-sidebar-foreground truncate">用户名</p>
            <p className="text-xs text-sidebar-foreground/60 truncate">user@example.com</p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start gap-2 text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground"
        >
          <LogOut className="h-4 w-4" />
          退出登录
        </Button>
      </div>
    </motion.div>
  )
}