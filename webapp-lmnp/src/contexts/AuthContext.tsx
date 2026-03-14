import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi } from '../services/api'

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  is_verified: boolean
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, firstName: string, lastName: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      // Verify token and get user profile
      authApi.getProfile()
        .then((profile: User) => {
          setUser(profile)
        })
        .catch(() => {
          // Token is invalid
          localStorage.removeItem('token')
          setToken(null)
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [token])

  const login = async (email: string, password: string) => {
    const response = await authApi.authenticate({
      email,
      password,
      create: false
    })

    if (response.success && response.token) {
      setToken(response.token)
      localStorage.setItem('token', response.token)
      setUser(response.user_profile)
    } else {
      throw new Error(response.error || 'Login failed')
    }
  }

  const register = async (email: string, password: string, firstName: string, lastName: string) => {
    const response = await authApi.register({
      email,
      password,
      first_name: firstName,
      last_name: lastName
    })

    if (response.success && response.token) {
      setToken(response.token)
      localStorage.setItem('token', response.token)
      setUser(response.user_profile)
    } else {
      throw new Error(response.error || 'Registration failed')
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isAuthenticated: !!user, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
