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

// Command Status Types
export interface CommandStatus {
  command_id: string
  shell_command: string
  args: Record<string, unknown>
  exit_state: number
  stdout: string | null
  stderr: string | null
  created_at?: string
  started_at?: string | null
  completed_at?: string | null
}

export interface MergePdfsResult {
  merged_file_id: string
}

// Process API (for file processing)
export const processApi = {
  // Create MergePdfs command via file upload
  createMergePdfsCommand: async (files: File[]): Promise<{ command_id: string }> => {
    const formData = new FormData()
    
    files.forEach((file) => {
      formData.append('files', file)
    })

    const response = await api.post('/api/mergePdfs', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Create SplitPdf command via file upload
  createSplitPdfCommand: async (file: File): Promise<{ command_id: string }> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/api/splitPdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Create MergeImages command via file upload
  createMergeImagesCommand: async (files: File[]): Promise<{ command_id: string }> => {
    const formData = new FormData()
    
    files.forEach((file) => {
      formData.append('files', file)
    })

    const response = await api.post('/api/mergeImages', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Create XlsToPdf command via file upload
  createXlsToPdfCommand: async (files: File[]): Promise<{ command_id: string }> => {
    const formData = new FormData()
    
    files.forEach((file) => {
      formData.append('files', file)
    })

    const response = await api.post('/api/xlsToPdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Create YouTube Summary command via URL
  createYoutubeSummaryCommand: async (url: string): Promise<{ command_id: string }> => {
    const response = await api.post('/api/youtubeSummary', { url })
    return response.data
  },

  // Get command status
  getCommandStatus: async (commandId: string): Promise<CommandStatus> => {
    const response = await api.get(`/api/command/${commandId}`)
    return response.data.command  // Extract the command data from the wrapper
  },

  // Build download URL for processed files
  getFileDownloadUrl: (fileId: string): string => {
    return `${API_BASE_URL}/api/processed-files/${fileId}`
  },

  // Legacy API methods (keep for backwards compatibility with other tools)
  create: async (data: {
    category: string
    tool: string
    files: File[]
  }, token: string) => {
    // Route to appropriate API based on tool
    if (data.category === 'merge' && data.tool === 'merge-pdf') {
      const result = await processApi.createMergePdfsCommand(data.files)
      return {
        success: true,
        processId: result.command_id, // Map to legacy field name
        command_id: result.command_id
      }
    }
    
    // For other tools, use legacy endpoint (to be implemented)
    const formData = new FormData()
    formData.append('category', data.category)
    formData.append('tool', data.tool)
    
    data.files.forEach((file, index) => {
      formData.append(`files[${index}]`, file)
    })

    const response = await api.post('/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`,
      },
    })
    return response.data
  },

  get: async (commandId: string) => {
    const status = await processApi.getCommandStatus(commandId)
    
    // Transform to legacy format for compatibility
    return {
      success: true,
      process: {
        id: status.command_id,
        status: status.exit_state === -1 ? 'processing' : 
                status.exit_state === 0 ? 'completed' : 'failed',
        progress: status.exit_state === -1 ? 50 : 100,
        error: status.stderr,
        command_status: status // Include raw status for new logic
      }
    }
  },

  download: async (commandId: string) => {
    // For MergePdfs, we need to get the merged_file_id first
    const status = await processApi.getCommandStatus(commandId)
    
    if (status.exit_state === 0 && status.stdout) {
      try {
        const result: MergePdfsResult = JSON.parse(status.stdout)
        const downloadUrl = processApi.getFileDownloadUrl(result.merged_file_id)
        
        // Return a response-like object for compatibility
        const response = await fetch(downloadUrl)
        return {
          data: await response.blob(),
          headers: {
            'content-disposition': `attachment; filename="merged.pdf"`
          }
        }
      } catch {
        throw new Error('Failed to parse command result')
      }
    } else {
      throw new Error('Command not completed successfully')
    }
  },
}

export { api }
