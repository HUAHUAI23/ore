import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Eye, EyeOff, Loader2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { LoginFormValues, RegisterFormValues } from '@/validation/auth'
import { loginSchema, registerSchema } from '@/validation/auth'

import { useLogin, useRegister } from './hook'

export function AuthForm() {
  const [isLogin, setIsLogin] = useState(true)
  const [showPassword, setShowPassword] = useState(false)

  const loginMutation = useLogin()
  const registerMutation = useRegister()

  const loginForm = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      name: '',
      password: '',
    },
  })

  const registerForm = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: '',
      password: '',
      nickname: '',
      email: '',
      phone: '',
    },
  })


  const onLoginSubmit = (data: LoginFormValues) => {
    loginMutation.mutate(data)
  }

  const onRegisterSubmit = (data: RegisterFormValues) => {
    const submitData = {
      ...data,
      email: data.email || undefined,
      phone: data.phone || undefined,
      nickname: data.nickname || undefined,
    }
    registerMutation.mutate(submitData)
  }

  const toggleMode = () => {
    setIsLogin(!isLogin)
    loginForm.reset()
    registerForm.reset()
  }

  const isLoading = loginMutation.isPending || registerMutation.isPending

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-center">
              {isLogin ? '登录账户' : '创建账户'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={
                isLogin
                  ? loginForm.handleSubmit(onLoginSubmit)
                  : registerForm.handleSubmit(onRegisterSubmit)
              }
              className="space-y-4"
            >
              {/* 用户名 */}
              <div>
                <Label htmlFor="name">用户名</Label>
                <Input
                  id="name"
                  type="text"
                  autoComplete="username"
                  {...(isLogin ? loginForm.register('name') : registerForm.register('name'))}
                  className={(isLogin ? loginForm.formState.errors.name : registerForm.formState.errors.name) ? 'border-red-500' : ''}
                />
                {(isLogin ? loginForm.formState.errors.name : registerForm.formState.errors.name) && (
                  <p className="mt-1 text-sm text-red-600">
                    {(isLogin ? loginForm.formState.errors.name : registerForm.formState.errors.name)?.message}
                  </p>
                )}
              </div>

              {/* 密码 */}
              <div>
                <Label htmlFor="password">密码</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete={isLogin ? 'current-password' : 'new-password'}
                    {...(isLogin ? loginForm.register('password') : registerForm.register('password'))}
                    className={`pr-10 ${(isLogin ? loginForm.formState.errors.password : registerForm.formState.errors.password) ? 'border-red-500' : ''}`}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                {(isLogin ? loginForm.formState.errors.password : registerForm.formState.errors.password) && (
                  <p className="mt-1 text-sm text-red-600">
                    {(isLogin ? loginForm.formState.errors.password : registerForm.formState.errors.password)?.message}
                  </p>
                )}
              </div>

              {/* 注册时的额外字段 */}
              {!isLogin && (
                <>
                  {/* 昵称 */}
                  <div>
                    <Label htmlFor="nickname">昵称（可选）</Label>
                    <Input
                      id="nickname"
                      type="text"
                      {...registerForm.register('nickname')}
                      className={registerForm.formState.errors.nickname ? 'border-red-500' : ''}
                    />
                    {registerForm.formState.errors.nickname && (
                      <p className="mt-1 text-sm text-red-600">{registerForm.formState.errors.nickname.message}</p>
                    )}
                  </div>

                  {/* 邮箱 */}
                  <div>
                    <Label htmlFor="email">邮箱（可选）</Label>
                    <Input
                      id="email"
                      type="email"
                      autoComplete="email"
                      {...registerForm.register('email')}
                      className={registerForm.formState.errors.email ? 'border-red-500' : ''}
                    />
                    {registerForm.formState.errors.email && (
                      <p className="mt-1 text-sm text-red-600">{registerForm.formState.errors.email.message}</p>
                    )}
                  </div>

                  {/* 手机号 */}
                  <div>
                    <Label htmlFor="phone">手机号（可选）</Label>
                    <Input
                      id="phone"
                      type="tel"
                      autoComplete="tel"
                      {...registerForm.register('phone')}
                      className={registerForm.formState.errors.phone ? 'border-red-500' : ''}
                    />
                    {registerForm.formState.errors.phone && (
                      <p className="mt-1 text-sm text-red-600">{registerForm.formState.errors.phone.message}</p>
                    )}
                  </div>
                </>
              )}

              {/* 提交按钮 */}
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white hover:bg-blue-700"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {isLogin ? '登录中...' : '注册中...'}
                  </>
                ) : (
                  isLogin ? '登录' : '注册'
                )}
              </Button>
            </form>

            {/* 切换登录/注册模式 */}
            <div className="mt-6 text-center">
              <Button
                variant="ghost"
                onClick={toggleMode}
                className="text-sm"
              >
                {isLogin ? '没有账户？立即注册' : '已有账户？立即登录'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}