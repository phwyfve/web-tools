import { useAuth } from '../contexts/AuthContext'
import { categories } from '../config/tools'
import { Link, useLocation } from 'react-router-dom'
import type { ReactNode } from 'react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth()
  const location = useLocation()

  const isAuthPage = location.pathname === '/login' || location.pathname === '/register'

  if (isAuthPage) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center">
        <div className="max-w-md mx-auto">
          {children}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Web Tools</h1>
            </Link>

            {/* Navigation */}
            {user && (
              <nav className="flex items-center space-x-6">
                {categories.map((category) => (
                  <Link
                    key={category.id}
                    to={`/#${category.id}`}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${category.color} hover:bg-gray-100`}
                  >
                    {category.name}
                  </Link>
                ))}
                
                {/* User Menu */}
                <div className="flex items-center space-x-4 ml-6 pl-6 border-l">
                  <span className="text-sm text-gray-700">
                    Hello, {user.first_name}
                  </span>
                  <button
                    onClick={logout}
                    className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    Logout
                  </button>
                </div>
              </nav>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}
