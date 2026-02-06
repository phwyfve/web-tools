import { Download, RefreshCw } from 'lucide-react'
import { processApi } from '../../services/api'

interface DownloadSectionProps {
  fileId: string
  filename: string
  onReset: () => void
  title?: string
  description?: string
  label?: string
}

export default function DownloadSection({
  fileId,
  filename,
  onReset,
  title = 'Your file is ready!',
  description = 'Click the button below to download your processed file.',
  label = 'Download File'
}: DownloadSectionProps) {
  const handleDownload = async () => {
    try {
      console.log('📥 Downloading file:', fileId, filename)
      
      // Get the download URL
      const downloadUrl = processApi.getFileDownloadUrl(fileId)
      console.log('🔗 Download URL:', downloadUrl)

      // Create a temporary link and trigger download
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      console.log('✅ Download triggered successfully')
    } catch (err: any) {
      console.error('❌ Download failed:', err)
      alert(`Download failed: ${err.message || 'Unknown error'}`)
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-12">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <Download className="h-8 w-8 text-green-600" />
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
          <p className="text-gray-600">{description}</p>
        </div>

        {/* File info */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{filename}</p>
              <p className="text-xs text-gray-500 mt-1">File ID: {fileId}</p>
            </div>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={handleDownload}
            className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="h-5 w-5" />
            {label}
          </button>

          <button
            onClick={onReset}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="h-5 w-5" />
            Process Another
          </button>
        </div>

        {/* Help text */}
        <p className="text-xs text-gray-500 text-center mt-6">
          Having trouble downloading? Try right-clicking the Download button and selecting "Save link as..."
        </p>
      </div>
    </div>
  )
}
