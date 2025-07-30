import { Link } from '@tanstack/react-router'
import { LogOut, User } from 'lucide-react'

import { useCurrentUser, useLogout } from '@/feature/auth/hook'
import { useAuthStore } from '@/store/auth'

export default function Header() {
  const { isAuthenticated } = useAuthStore()
  const { data: user } = useCurrentUser()
  const logout = useLogout()

  if (!isAuthenticated) {
    return null
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Brand */}
          <nav className="flex items-center">
            <Link
              to="/"
              className="text-xl font-bold text-gray-900 hover:text-gray-700"
            >
              ORE
            </Link>
          </nav>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {user && (
              <div className="flex items-center space-x-2 text-sm text-gray-700">
                <User className="h-4 w-4" />
                <span>{user.nickname || user.name}</span>
              </div>
            )}

            <button
              onClick={logout}
              className="flex items-center space-x-1 px-3 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            >
              <LogOut className="h-4 w-4" />
              <span>退出</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
