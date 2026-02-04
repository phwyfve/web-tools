import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import UploadSection from '../components/workflow/UploadSection'
import WaitSection from '../components/workflow/WaitSection'
import DownloadSection from '../components/workflow/DownloadSection'
import { processApi } from '../services/api'

export default function XlsToPdf() {
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
      alert('Please select at least 1 Excel file')
      return
    }

    try {
      setUploading(true)
      console.log('📤 Uploading Excel files for conversion to PDF:', files.map(f => f.name))

      const response = await processApi.createXlsToPdfCommand(files)
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
        filename="excel_converted.pdf"
        onReset={handleReset}
        title="Your Excel file has been converted to PDF!"
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Excel to PDF</h1>
          <p className="text-gray-600">
            Convert Excel spreadsheets to PDF format. Upload one or more Excel files.
          </p>
        </div>

        <UploadSection
          acceptedFormats={['.xls', '.xlsx', '.xlsm']}
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
              className="w-full px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? 'Uploading...' : `Convert ${files.length} Excel File${files.length > 1 ? 's' : ''} to PDF`}
            </button>
          </div>
        )}
      </div>

      {/* Info section */}
      <div className="mt-8 bg-green-50 rounded-lg p-6">
        <h3 className="font-semibold text-green-900 mb-2">How it works:</h3>
        <ol className="list-decimal list-inside space-y-1 text-green-800">
          <li>Select one or more Excel files (.xls, .xlsx, .xlsm)</li>
          <li>Each sheet in your workbook becomes pages in the PDF</li>
          <li>Tables are formatted with headers and alternating row colors</li>
          <li>Wide sheets automatically use landscape orientation</li>
          <li>Download your professionally formatted PDF file</li>
        </ol>
        <div className="mt-4 p-3 bg-white rounded border border-green-200">
          <p className="text-sm text-green-900">
            <strong>💡 Tip:</strong> Multiple Excel files will be combined into a single PDF with all sheets from all files.
          </p>
        </div>
      </div>
    </div>
  )
}
