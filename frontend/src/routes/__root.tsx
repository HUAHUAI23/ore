import { createRootRoute, Outlet, redirect } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'

import { useAuthStore } from '@/store/auth'


export const Route = createRootRoute({
  beforeLoad: ({ location }) => {
    // 检查用户是否已登录
    const { isAuthenticated } = useAuthStore.getState()

    // 如果用户未登录且不在认证页面，重定向到登录页
    if (!isAuthenticated && location.pathname !== '/auth') {
      throw redirect({ to: '/auth' })
    }
  },
  component: RootComponent,
})

function RootComponent() {
  return (
    <>
      <Outlet />
      <TanStackRouterDevtools />
    </>
  )
}
