import { useState, useCallback, useEffect } from 'react'
import { Upload as UploadIcon, File, AlertCircle, X } from 'lucide-react'

interface UploadSectionProps {
  acceptedFormats: string[]
  multiple?: boolean
  onFilesSelected: (files: File[]) => void
  onError?: (error: string) => void
  uploadButtonText?: string
  title?: string
  description?: string
}

export default function UploadSection({
  acceptedFormats,
  multiple = false,
  onFilesSelected,
  onError,
  uploadButtonText = 'Upload Files',
  title = 'Upload Files',
  description = 'Drag and drop your files here, or click to browse'
}: UploadSectionProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Notify parent when files change
  useEffect(() => {
    if (selectedFiles.length > 0) {
      onFilesSelected(selectedFiles)
    }
  }, [selectedFiles, onFilesSelected])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files) {
      handleFileSelect(e.dataTransfer.files)
    }
  }, [acceptedFormats, multiple])

  const handleFileSelect = (fileList: FileList) => {
    const files = Array.from(fileList)
    const validFiles: File[] = []
    const invalidFiles: string[] = []

    files.forEach((file) => {
      const extension = '.' + file.name.split('.').pop()?.toLowerCase()
      if (acceptedFormats.includes(extension)) {
        validFiles.push(file)
      } else {
        invalidFiles.push(file.name)
      }
    })

    if (invalidFiles.length > 0) {
      const errMsg = `Invalid files: ${invalidFiles.join(', ')}`
      setError(errMsg)
      onError?.(errMsg)
      return
    }

    if (!multiple && validFiles.length > 1) {
      const errMsg = 'Please select only one file'
      setError(errMsg)
      onError?.(errMsg)
      return
    }

    setSelectedFiles(multiple ? [...selectedFiles, ...validFiles] : validFiles)
    setError(null)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFileSelect(e.target.files)
    }
  }

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index)
    setSelectedFiles(newFiles)
    onFilesSelected(newFiles)
  }

  return (
    <div>
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-start">
          <AlertCircle className="h-5 w-5 mr-2 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Accepted Formats */}
      <div className="mb-6">
        <p className="text-sm text-gray-600 mb-2">Accepted formats:</p>
        <div className="flex flex-wrap gap-2">
          {acceptedFormats.map((format) => (
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
        onDragOver={handleDrag}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <UploadIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-700 mb-2">
          Drop files here or click to browse
        </p>
        <p className="text-sm text-gray-500 mb-4">
          {multiple ? 'You can upload multiple files at once' : 'Upload one file'}
        </p>
        <input
          type="file"
          multiple={multiple}
          accept={acceptedFormats.join(',')}
          onChange={handleFileInputChange}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer"
        >
          Select {multiple ? 'Files' : 'File'}
        </label>
      </div>

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="mt-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Selected Files ({selectedFiles.length})
          </h3>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="border border-gray-200 rounded-lg p-4 flex items-center justify-between"
              >
                <div className="flex items-center space-x-3">
                  <File className="h-6 w-6 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-900">{file.name}</p>
                    <p className="text-sm text-gray-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-600 hover:text-red-700 p-2"
                  title="Remove file"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
