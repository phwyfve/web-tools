import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth API
export const authApi = {
  register: async (data: {
    email: string
    password: string
    first_name: string
    last_name: string
  }) => {
    const response = await api.post('/api/register', data)
    return response.data
  },

  authenticate: async (data: {
    email: string
    password: string
    create?: boolean
  }) => {
    const response = await api.post('/api/authenticate', data)
    return response.data
  },

  getProfile: async () => {
    const response = await api.get('/api/user-profile')
    return response.data
  },
}

export { api }
