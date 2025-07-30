import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { toast } from 'sonner';

import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/auth';
import type { LoginRequest, RegisterRequest } from '@/types/auth';

// Query keys
export const authKeys = {
  all: ['auth'] as const,
  currentUser: () => [...authKeys.all, 'currentUser'] as const,
};

// 获取当前用户信息的 hook
export const useCurrentUser = () => {
  const { isAuthenticated } = useAuthStore();
  
  return useQuery({
    queryKey: authKeys.currentUser(),
    queryFn: () => authApi.getCurrentUser(),
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: (failureCount, error: ApiError) => {
      // 如果是 401 错误，不重试
      if (error.error_code === 401) {
        return false;
      }
      return failureCount < 3;
    },
  });
};

// 登录 hook
export const useLogin = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { login } = useAuthStore();

  return useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response) => {
      // 保存用户信息和 token
      login(response.access_token, response.user);
      
      // 更新查询缓存
      queryClient.setQueryData(authKeys.currentUser(), response.user);
      
      // 显示成功消息
      toast.success('登录成功');
      
      // 跳转到主页
      navigate({ to: '/' });
    },
    onError: (error: ApiError) => {
      console.error('Login failed:', error);
      toast.error(error.message || '登录失败，请检查用户名和密码');
    },
  });
};

// 注册 hook
export const useRegister = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { login } = useAuthStore();

  return useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: (response) => {
      // 自动登录用户
      login(response.access_token, response.user);
      
      // 更新查询缓存
      queryClient.setQueryData(authKeys.currentUser(), response.user);
      
      // 显示成功消息
      toast.success('注册成功，欢迎使用！');
      
      // 跳转到主页
      navigate({ to: '/' });
    },
    onError: (error: ApiError) => {
      console.error('Registration failed:', error);
      toast.error(error.message || '注册失败，请稍后重试');
    },
  });
};

// 登出 hook
export const useLogout = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { logout } = useAuthStore();

  return () => {
    // 清除用户状态
    logout();
    
    // 清除所有查询缓存
    queryClient.clear();
    
    // 显示成功消息
    toast.success('已安全退出');
    
    // 跳转到登录页
    navigate({ to: '/auth' });
  };
};