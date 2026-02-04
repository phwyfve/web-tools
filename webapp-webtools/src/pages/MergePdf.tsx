import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import UploadSection from '../components/workflow/UploadSection'
import WaitSection from '../components/workflow/WaitSection'
import DownloadSection from '../components/workflow/DownloadSection'
import { processApi } from '../services/api'

export default function MergePdf() {
  const [searchParams, setSearchParams] = useSearchParams()
  const commandId = searchParams.get('command')

  const [uploading, setUploading] = useState(false)
  const [files, setFiles] = useState<File[]>([])
  const [result, setResult] = useState<{
    merged_file_id: string
  } | null>(null)

  // Handle file selection from UploadSection
  const handleFilesSelected = (selectedFiles: File[]) => {
    setFiles(selectedFiles)
  }

  // Handle upload and command creation
  const handleUpload = async () => {
    if (files.length < 2) {
      alert('Please select at least 2 PDF files to merge')
      return
    }

    try {
      setUploading(true)
      console.log('📤 Uploading files for merge:', files.map(f => f.name))

      const response = await processApi.createMergePdfsCommand(files)
      console.log('✅ Command created:', response.command_id)

      // Update URL with command ID
      setSearchParams({ command: response.command_id })
    } catch (err: any) {
      console.error('❌ Upload failed:', err)
      alert(`Upload failed: ${err.message || 'Unknown error'}`)
    } finally {
      setUploading(false)
    }
  }

  // Handle processing completion
  const handleComplete = (commandResult: any) => {
    console.log('✅ Processing complete, result:', commandResult)
    setResult(commandResult)
  }

  // Handle reset to start over
  const handleReset = () => {
    setSearchParams({})
    setFiles([])
    setResult(null)
  }

  // Render different sections based on state
  if (result) {
    // Download phase
    return (
      <DownloadSection
        fileId={result.merged_file_id}
        filename="merged.pdf"
        onReset={handleReset}
        title="Your PDFs have been merged!"
        description="Click the button below to download your merged PDF file."
      />
    )
  }

  if (commandId) {
    // Processing/waiting phase
    return (
      <WaitSection
        commandId={commandId}
        onComplete={handleComplete}
        onError={(error) => {
          alert(`Processing failed: ${error}`)
          handleReset()
        }}
      />
    )
  }

  // Upload phase (default)
  return (
    <div className="max-w-4xl mx-auto py-12 px-4">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Merge PDFs</h1>
          <p className="text-gray-600">
            Combine multiple PDF files into a single document. Upload at least 2 PDF files.
          </p>
        </div>

        <UploadSection
          acceptedFormats={['.pdf']}
          multiple={true}
          onFilesSelected={handleFilesSelected}
          onError={(error: string) => alert(error)}
          uploadButtonText="Merge PDFs"
        />

        {/* Upload button */}
        {files.length > 0 && (
          <div className="mt-6">
            <button
              onClick={handleUpload}
              disabled={uploading || files.length < 2}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? 'Uploading...' : `Merge ${files.length} PDF${files.length > 1 ? 's' : ''}`}
            </button>
            
            {files.length < 2 && (
              <p className="text-sm text-amber-600 text-center mt-2">
                Please select at least 2 PDF files to merge
              </p>
            )}
          </div>
        )}
      </div>

      {/* Info section */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">How it works:</h3>
        <ol className="list-decimal list-inside space-y-1 text-blue-800">
          <li>Select 2 or more PDF files using the upload area</li>
          <li>Click "Merge PDFs" to start processing</li>
          <li>Wait while your files are being merged</li>
          <li>Download your merged PDF file</li>
        </ol>
      </div>
    </div>
  )
}
