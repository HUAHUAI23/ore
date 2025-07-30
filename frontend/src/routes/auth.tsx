import { createFileRoute, redirect } from '@tanstack/react-router';

import { AuthForm } from '@/feature/auth/auth-form';
import { useAuthStore } from '@/store/auth';

export const Route = createFileRoute('/auth')({
  beforeLoad: () => {
    // 如果用户已登录，重定向到首页
    const { isAuthenticated } = useAuthStore.getState();
    if (isAuthenticated) {
      throw redirect({ to: '/' });
    }
  },
  component: AuthPage,
});

function AuthPage() {
  return <AuthForm />;
}