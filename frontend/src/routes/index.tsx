import { createFileRoute } from '@tanstack/react-router';

import { useCurrentUser } from '@/feature/auth/hook';

export const Route = createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  const { data: user, isLoading } = useCurrentUser();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">
            欢迎使用 ORE 系统
          </h1>
          
          {user && (
            <div className="bg-white rounded-lg shadow p-6 max-w-md mx-auto">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                用户信息
              </h2>
              <div className="space-y-2 text-left">
                <p><span className="font-medium">用户名:</span> {user.name}</p>
                <p><span className="font-medium">昵称:</span> {user.nickname}</p>
                {user.email && (
                  <p><span className="font-medium">邮箱:</span> {user.email}</p>
                )}
                {user.phone && (
                  <p><span className="font-medium">手机:</span> {user.phone}</p>
                )}
                <p><span className="font-medium">状态:</span> 
                  <span className={user.is_active ? 'text-green-600' : 'text-red-600'}>
                    {user.is_active ? '正常' : '禁用'}
                  </span>
                </p>
                <p><span className="font-medium">注册时间:</span> 
                  {new Date(user.created_at).toLocaleString('zh-CN')}
                </p>
                {user.last_login && (
                  <p><span className="font-medium">最后登录:</span> 
                    {new Date(user.last_login).toLocaleString('zh-CN')}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}