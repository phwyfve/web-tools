import { useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { processApi } from '../services/api'
import { getCategoryById, getToolById } from '../config/tools'

export default function Upload() {
  const { category: categoryId, tool: toolId } = useParams<{ category: string; tool: string }>()
  const navigate = useNavigate()
  const { token } = useAuth()
  const { addToast } = useToast()

  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [dragOver, setDragOver] = useState(false)
  const [processing, setProcessing] = useState(false)

  const category = getCategoryById(categoryId!)
  const tool = getToolById(categoryId!, toolId!)

  const handleFileSelect = useCallback((files: FileList | null) => {
    if (!files || !tool) return

    const validFiles: File[] = []
    const invalidFiles: string[] = []

    Array.from(files).forEach((file) => {
      const extension = '.' + file.name.split('.').pop()?.toLowerCase()
      if (tool.acceptedFormats.includes(extension)) {
        validFiles.push(file)
      } else {
        invalidFiles.push(file.name)
      }
    })

    if (invalidFiles.length > 0) {
      addToast({
        title: 'Invalid file format',
        description: `Files not supported: ${invalidFiles.join(', ')}`,
        variant: 'destructive',
      })
    }

    setSelectedFiles((prev) => [...prev, ...validFiles])
  }, [tool?.acceptedFormats, addToast, tool])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragOver(false)
      handleFileSelect(e.dataTransfer.files)
    },
    [handleFileSelect]
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  if (!category || !tool) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Tool not found</h1>
        <p className="text-gray-600 mb-8">The requested tool could not be found.</p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Go back to home
        </button>
      </div>
    )
  }

  const handleProcess = async () => {
    if (selectedFiles.length === 0) return

    setProcessing(true)
    try {
      let commandId: string

      // Route to appropriate API based on tool
      if (categoryId === 'merge' && toolId === 'merge-pdf') {
        const response = await processApi.createMergePdfsCommand(selectedFiles)
        commandId = response.command_id
      } else {
        // For other tools, use legacy API
        const response = await processApi.create(
          {
            category: categoryId!,
            tool: toolId!,
            files: selectedFiles,
          },
          token!
        )
        
        if (response.success) {
          commandId = response.command_id || response.processId
        } else {
          addToast({
            title: 'Processing failed',
            description: response.error || 'Failed to start processing',
            variant: 'destructive',
          })
          return
        }
      }

      // Navigate to wait page with command_id
      navigate(`/wait/${commandId}`)
      
    } catch {
      addToast({
        title: 'Processing failed',
        description: 'Network error occurred',
        variant: 'destructive',
      })
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <nav className="text-sm text-gray-500 mb-4">
          <button onClick={() => navigate('/')} className="hover:text-blue-600">
            Home
          </button>
          <span className="mx-2">/</span>
          <span className={category.color}>{category.name}</span>
          <span className="mx-2">/</span>
          <span className="text-gray-900">{tool.name}</span>
        </nav>

        <div className="flex items-start space-x-4">
          <div className="text-4xl">{tool.icon}</div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{tool.name}</h1>
            <p className="text-gray-600 text-lg">{tool.description}</p>
          </div>
        </div>
      </div>

      {/* File Upload Area */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Files</h2>
        
        {/* Accepted Formats */}
        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-2">Accepted formats:</p>
          <div className="flex flex-wrap gap-2">
            {tool.acceptedFormats.map((format) => (
              <span
                key={format}
                className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full font-mono"
              >
                {format}
              </span>
            ))}
          </div>
        </div>

        {/* Drop Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragOver
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <div className="space-y-4">
            <div className="text-4xl text-gray-400">📁</div>
            <div>
              <p className="text-lg font-medium text-gray-900">
                Drop files here or click to select
              </p>
              <p className="text-gray-500">
                You can upload multiple files at once
              </p>
            </div>
            <input
              type="file"
              multiple
              accept={tool.acceptedFormats.join(',')}
              onChange={(e) => handleFileSelect(e.target.files)}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="btn-primary inline-block cursor-pointer">
              Select Files
            </label>
          </div>
        </div>

        {/* Selected Files */}
        {selectedFiles.length > 0 && (
          <div className="mt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Selected Files ({selectedFiles.length})
            </h3>
            <div className="space-y-2">
              {selectedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-xl">📄</div>
                    <div>
                      <div className="font-medium text-gray-900">{file.name}</div>
                      <div className="text-sm text-gray-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="text-red-500 hover:text-red-700 p-1"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Process Button */}
        {selectedFiles.length > 0 && (
          <div className="mt-8 flex justify-center">
            <button
              onClick={handleProcess}
              disabled={processing}
              className="btn-primary px-8 py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {processing ? 'Processing...' : `Process ${selectedFiles.length} file${selectedFiles.length !== 1 ? 's' : ''}`}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
