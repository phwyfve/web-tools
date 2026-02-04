import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { processApi, type CommandStatus, type MergePdfsResult } from '../services/api'

interface ProcessStatus {
  id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message?: string
  error?: string
  command_status?: CommandStatus
  merged_file_id?: string
}

export default function Wait() {
  const { processId: commandId } = useParams<{ processId: string }>()
  const navigate = useNavigate()
  
  const [processStatus, setProcessStatus] = useState<ProcessStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!commandId) {
      navigate('/')
      return
    }

    const pollProcess = async () => {
      try {
        const commandStatus = await processApi.getCommandStatus(commandId)
        
        // Transform command status to process status
        const status: ProcessStatus = {
          id: commandStatus.command_id,
          status: commandStatus.exit_state === -1 ? 'processing' : 
                  commandStatus.exit_state === 0 ? 'completed' : 'failed',
          progress: commandStatus.exit_state === -1 ? 50 : 100,
          error: commandStatus.stderr || undefined,
          command_status: commandStatus
        }

        // For MergePdfs success, extract merged_file_id
        if (commandStatus.exit_state === 0 && commandStatus.stdout && 
            commandStatus.shell_command === 'MergePdfs') {
          try {
            const result: MergePdfsResult = JSON.parse(commandStatus.stdout)
            status.merged_file_id = result.merged_file_id
          } catch {
            // Failed to parse stdout, but still show as completed
          }
        }

        setProcessStatus(status)
        
        if (status.status === 'completed') {
          // Wait a moment to show completion, then redirect
          setTimeout(() => {
            navigate(`/download/${commandId}`, { 
              state: { 
                merged_file_id: status.merged_file_id,
                command_status: commandStatus
              } 
            })
          }, 1500)
        } else if (status.status === 'failed') {
          setError(status.error || 'Processing failed')
        }
        
      } catch {
        setError('Network error occurred')
      } finally {
        setLoading(false)
      }
    }

    // Initial poll
    pollProcess()

    // Set up polling every 2 seconds
    const pollIntervalId = setInterval(pollProcess, 2000)

    return () => {
      clearInterval(pollIntervalId)
    }
  }, [commandId, navigate])

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading process status...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="text-4xl mb-4">❌</div>
        <h1 className="text-2xl font-bold text-red-600 mb-4">Processing Failed</h1>
        <p className="text-gray-600 mb-8">{error}</p>
        <div className="space-x-4">
          <button onClick={() => navigate('/')} className="btn-primary">
            Go Home
          </button>
          <button onClick={() => navigate(-1)} className="btn-secondary">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (!processStatus) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Process not found</h1>
        <p className="text-gray-600 mb-8">The requested process could not be found.</p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Go Home
        </button>
      </div>
    )
  }

  const getStatusInfo = () => {
    switch (processStatus.status) {
      case 'pending':
        return {
          icon: '⏳',
          title: 'Processing Queued',
          description: 'Your files are in the processing queue',
          color: 'text-yellow-600'
        }
      case 'processing':
        return {
          icon: '⚡',
          title: 'Processing Files',
          description: 'Your files are being processed',
          color: 'text-blue-600'
        }
      case 'completed':
        return {
          icon: '✅',
          title: 'Processing Complete',
          description: 'Your files have been processed successfully',
          color: 'text-green-600'
        }
      case 'failed':
        return {
          icon: '❌',
          title: 'Processing Failed',
          description: 'An error occurred during processing',
          color: 'text-red-600'
        }
      default:
        return {
          icon: '❓',
          title: 'Unknown Status',
          description: 'Unknown processing status',
          color: 'text-gray-600'
        }
    }
  }

  const statusInfo = getStatusInfo()

  return (
    <div className="max-w-2xl mx-auto py-12">
      <div className="card text-center">
        {/* Status Icon */}
        <div className="text-6xl mb-6">{statusInfo.icon}</div>

        {/* Status Title */}
        <h1 className={`text-3xl font-bold mb-4 ${statusInfo.color}`}>
          {statusInfo.title}
        </h1>

        {/* Command ID */}
        <p className="text-sm text-gray-500 mb-2">Command ID</p>
        <p className="font-mono text-sm text-gray-700 mb-6 bg-gray-100 px-3 py-1 rounded">
          {commandId}
        </p>

        {/* Description */}
        <p className="text-gray-600 mb-8 text-lg">
          {statusInfo.description}
        </p>

        {/* Progress Bar */}
        {processStatus.status !== 'failed' && (
          <div className="mb-8">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Progress</span>
              <span className="text-sm font-medium text-gray-900">
                {processStatus.progress}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  processStatus.status === 'completed' 
                    ? 'bg-green-500' 
                    : 'bg-blue-500'
                }`}
                style={{ width: `${processStatus.progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Status Message */}
        {processStatus.message && (
          <p className="text-gray-600 mb-6 bg-gray-50 p-3 rounded">
            {processStatus.message}
          </p>
        )}

        {/* Loading Animation for Active Processes */}
        {(processStatus.status === 'pending' || processStatus.status === 'processing') && (
          <div className="flex items-center justify-center space-x-2 mb-6">
            <div className="animate-bounce w-2 h-2 bg-blue-600 rounded-full"></div>
            <div className="animate-bounce w-2 h-2 bg-blue-600 rounded-full" style={{ animationDelay: '0.1s' }}></div>
            <div className="animate-bounce w-2 h-2 bg-blue-600 rounded-full" style={{ animationDelay: '0.2s' }}></div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-center space-x-4">
          {processStatus.status === 'completed' && (
            <p className="text-green-600 font-medium">
              Redirecting to download...
            </p>
          )}
          {processStatus.status === 'failed' && (
            <>
              <button onClick={() => navigate('/')} className="btn-primary">
                Go Home
              </button>
              <button onClick={() => navigate(-1)} className="btn-secondary">
                Try Again
              </button>
            </>
          )}
          {(processStatus.status === 'pending' || processStatus.status === 'processing') && (
            <button onClick={() => navigate('/')} className="btn-secondary">
              Go Home
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
