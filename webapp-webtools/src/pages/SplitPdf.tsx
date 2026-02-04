import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import UploadSection from '../components/workflow/UploadSection'
import WaitSection from '../components/workflow/WaitSection'
import DownloadSection from '../components/workflow/DownloadSection'
import { processApi } from '../services/api'

export default function SplitPdf() {
  const [searchParams, setSearchParams] = useSearchParams()
  const commandId = searchParams.get('command')

  const [uploading, setUploading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<{
    output_file_id: string
    output_filename?: string
    total_pages?: number
  } | null>(null)

  // Handle file selection from UploadSection
  const handleFilesSelected = (selectedFiles: File[]) => {
    setFile(selectedFiles[0])
  }

  // Handle upload and command creation
  const handleUpload = async () => {
    if (!file) {
      alert('Please select a PDF file to split')
      return
    }

    try {
      setUploading(true)
      console.log('📤 Uploading file for split:', file.name)

      const response = await processApi.createSplitPdfCommand(file)
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
    console.log('✅ Processing complete, full result:', commandResult)
    console.log('📦 Result structure:', JSON.stringify(commandResult, null, 2))
    
    // Handle both naming conventions (backward compatibility)
    const fileId = commandResult.output_file_id || commandResult.zip_file_id
    const filename = commandResult.output_filename || commandResult.zip_filename || 'split_pages.zip'
    
    console.log('📦 File ID:', fileId)
    console.log('📦 Filename:', filename)
    console.log('📦 Total pages:', commandResult.total_pages)
    
    if (!fileId) {
      console.error('❌ No file ID in result:', commandResult)
      alert('Error: No file ID received from server')
      return
    }
    
    setResult({
      output_file_id: fileId,
      output_filename: filename,
      total_pages: commandResult.total_pages
    })
  }

  // Handle reset to start over
  const handleReset = () => {
    setSearchParams({})
    setFile(null)
    setResult(null)
  }

  // Render different sections based on state
  if (result) {
    // Download phase
    return (
      <DownloadSection
        fileId={result.output_file_id}
        filename={result.output_filename || 'split_pages.zip'}
        onReset={handleReset}
        title="Your PDF has been split!"
        description={`Successfully split into ${result.total_pages || 'multiple'} pages. Download the ZIP file below.`}
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Split PDF</h1>
          <p className="text-gray-600">
            Extract individual pages from your PDF. Upload a PDF file to split into separate pages.
          </p>
        </div>

        <UploadSection
          acceptedFormats={['.pdf']}
          multiple={false}
          onFilesSelected={handleFilesSelected}
          onError={(error: string) => alert(error)}
          uploadButtonText="Split PDF"
        />

        {/* Upload button */}
        {file && (
          <div className="mt-6">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? 'Uploading...' : 'Split PDF into Pages'}
            </button>
          </div>
        )}
      </div>

      {/* Info section */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">How it works:</h3>
        <ol className="list-decimal list-inside space-y-1 text-blue-800">
          <li>Select a PDF file using the upload area</li>
          <li>Click "Split PDF into Pages" to start processing</li>
          <li>Wait while your PDF is being split into individual pages</li>
          <li>Download a ZIP file containing all pages as separate PDFs</li>
        </ol>
      </div>
    </div>
  )
}
