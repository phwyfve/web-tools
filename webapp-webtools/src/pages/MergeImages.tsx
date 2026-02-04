import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import UploadSection from '../components/workflow/UploadSection'
import WaitSection from '../components/workflow/WaitSection'
import DownloadSection from '../components/workflow/DownloadSection'
import { processApi } from '../services/api'

export default function MergeImages() {
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
    if (files.length < 1) {
      alert('Please select at least 1 image file')
      return
    }

    try {
      setUploading(true)
      console.log('📤 Uploading images for conversion to PDF:', files.map(f => f.name))

      const response = await processApi.createMergeImagesCommand(files)
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
        filename="merged_images.pdf"
        onReset={handleReset}
        title="Your images have been converted to PDF!"
        description="Click the button below to download your PDF file."
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Merge Images to PDF</h1>
          <p className="text-gray-600">
            Convert and combine multiple images into a single PDF document. Upload one or more image files.
          </p>
        </div>

        <UploadSection
          acceptedFormats={['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']}
          multiple={true}
          onFilesSelected={handleFilesSelected}
          onError={(error: string) => alert(error)}
          uploadButtonText="Convert to PDF"
        />

        {/* Upload button */}
        {files.length > 0 && (
          <div className="mt-6">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? 'Uploading...' : `Convert ${files.length} Image${files.length > 1 ? 's' : ''} to PDF`}
            </button>
          </div>
        )}
      </div>

      {/* Info section */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">How it works:</h3>
        <ol className="list-decimal list-inside space-y-1 text-blue-800">
          <li>Select one or more image files (JPG, PNG, BMP, GIF, TIFF)</li>
          <li>Each image will be converted to a PDF page</li>
          <li>Images are auto-oriented (portrait/landscape) based on their dimensions</li>
          <li>Aspect ratios are preserved - no distortion</li>
          <li>Download your PDF file with all images combined</li>
        </ol>
      </div>
    </div>
  )
}
