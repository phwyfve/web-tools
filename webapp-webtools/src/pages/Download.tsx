import { useState, useEffect } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useToast } from '../contexts/ToastContext'
import { processApi, type CommandStatus } from '../services/api'

interface ProcessResult {
  id: string
  status: 'completed' | 'failed'
  fileName?: string
  fileSize?: number
  createdAt: string
  processingTime?: number
  merged_file_id?: string
  command_status?: CommandStatus
}

export default function Download() {
  const { processId: commandId } = useParams<{ processId: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const { addToast } = useToast()
  
  const [processResult, setProcessResult] = useState<ProcessResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!commandId) {
      navigate('/')
      return
    }

    // Check if we have state from the Wait page
    const state = location.state as { merged_file_id?: string, command_status?: CommandStatus }
    
    if (state?.command_status) {
      // We have the command status from the Wait page
      const commandStatus = state.command_status
      
      if (commandStatus.exit_state === 0) {
        // Success - create process result from command status
        const result: ProcessResult = {
          id: commandStatus.command_id,
          status: 'completed',
          createdAt: new Date().toISOString(),
          merged_file_id: state.merged_file_id,
          command_status: commandStatus
        }
        setProcessResult(result)
        setLoading(false)
      } else {
        setError(commandStatus.stderr || 'Processing failed')
        setLoading(false)
      }
      return
    }

    // Fallback: fetch command status directly
    const fetchProcessResult = async () => {
      try {
        const commandStatus = await processApi.getCommandStatus(commandId)
        
        if (commandStatus.exit_state === 0) {
          // Success
          const result: ProcessResult = {
            id: commandStatus.command_id,
            status: 'completed',
            createdAt: new Date().toISOString(),
            command_status: commandStatus
          }
          
          // Try to extract merged_file_id from stdout if it's a MergePdfs command
          if (commandStatus.stdout && commandStatus.shell_command === 'MergePdfs') {
            try {
              const mergePdfsResult = JSON.parse(commandStatus.stdout)
              result.merged_file_id = mergePdfsResult.merged_file_id
            } catch {
              // Failed to parse, but still show as completed
            }
          }
          
          setProcessResult(result)
        } else if (commandStatus.exit_state === -1) {
          // Still processing, redirect to wait page
          navigate(`/wait/${commandId}`)
          return
        } else {
          // Failed
          setError(commandStatus.stderr || 'Processing failed')
        }
      } catch {
        setError('Failed to load process result')
      } finally {
        setLoading(false)
      }
    }

    fetchProcessResult()
  }, [commandId, location.state, navigate])

  const handleDownload = async () => {
    if (!commandId || !processResult?.merged_file_id) return

    setDownloading(true)
    try {
      const response = await processApi.download(commandId)
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // Get filename from response headers or use default
      const contentDisposition = response.headers['content-disposition']
      let filename = 'processed-file'
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '')
        }
      } else if (processResult?.fileName) {
        filename = processResult.fileName
      }
      
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      addToast({
        title: 'Download started',
        description: 'Your processed file is downloading',
        variant: 'success',
      })
    } catch {
      addToast({
        title: 'Download failed',
        description: 'Failed to download the processed file',
        variant: 'destructive',
      })
    } finally {
      setDownloading(false)
    }
  }

  const handleStartOver = () => {
    navigate('/')
  }

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading download information...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="text-4xl mb-4">❌</div>
        <h1 className="text-2xl font-bold text-red-600 mb-4">Download Not Available</h1>
        <p className="text-gray-600 mb-8">{error}</p>
        <div className="space-x-4">
          <button onClick={handleStartOver} className="btn-primary">
            Start Over
          </button>
          <button onClick={() => navigate(-1)} className="btn-secondary">
            Go Back
          </button>
        </div>
      </div>
    )
  }

  if (!processResult) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Process not found</h1>
        <p className="text-gray-600 mb-8">The requested process result could not be found.</p>
        <button onClick={handleStartOver} className="btn-primary">
          Start Over
        </button>
      </div>
    )
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatProcessingTime = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  return (
    <div className="max-w-2xl mx-auto py-12">
      <div className="card text-center">
        {/* Success Icon */}
        <div className="text-6xl mb-6">🎉</div>

        {/* Success Title */}
        <h1 className="text-3xl font-bold text-green-600 mb-4">
          Processing Complete!
        </h1>

        {/* Process Info */}
        <div className="bg-gray-50 rounded-lg p-6 mb-8 text-left">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Command ID:</span>
              <p className="font-mono text-gray-700 break-all">{commandId}</p>
            </div>
            <div>
              <span className="text-gray-500">Completed:</span>
              <p className="text-gray-700">
                {new Date(processResult.createdAt).toLocaleString()}
              </p>
            </div>
            {processResult.fileName && (
              <div>
                <span className="text-gray-500">File Name:</span>
                <p className="text-gray-700">{processResult.fileName}</p>
              </div>
            )}
            {processResult.fileSize && (
              <div>
                <span className="text-gray-500">File Size:</span>
                <p className="text-gray-700">{formatFileSize(processResult.fileSize)}</p>
              </div>
            )}
            {processResult.processingTime && (
              <div className="col-span-2">
                <span className="text-gray-500">Processing Time:</span>
                <p className="text-gray-700">{formatProcessingTime(processResult.processingTime)}</p>
              </div>
            )}
          </div>
        </div>

        {/* Download Section */}
        <div className="mb-8">
          <p className="text-gray-600 mb-6">
            Your file has been processed successfully. Click the button below to download it.
          </p>

          <button
            onClick={handleDownload}
            disabled={downloading}
            className="btn-primary px-8 py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed mb-4"
          >
            {downloading ? (
              <>
                <span className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                Downloading...
              </>
            ) : (
              <>
                📥 Download File
              </>
            )}
          </button>

          <p className="text-xs text-gray-500">
            Files are available for download for 24 hours
          </p>
        </div>

        {/* Actions */}
        <div className="flex justify-center space-x-4">
          <button onClick={handleStartOver} className="btn-secondary px-6 py-2">
            🔄 Start Over
          </button>
          <button onClick={() => navigate('/')} className="btn-secondary px-6 py-2">
            🏠 Go Home
          </button>
        </div>

        {/* Tips */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg text-left">
          <h3 className="font-medium text-blue-900 mb-2">💡 Tips</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Right-click the download button and select "Save As" to choose location</li>
            <li>• Files are automatically deleted after 24 hours for security</li>
            <li>• Need help? Contact support with your Process ID</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
