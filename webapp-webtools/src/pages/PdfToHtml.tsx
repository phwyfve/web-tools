import { useState } from 'react'
import WaitSection from '../components/workflow/WaitSection'
import DownloadSection from '../components/workflow/DownloadSection'
import { processApi } from '../services/api'

export default function PdfToHtml() {
  const [file, setFile] = useState<File | null>(null)
  const [commandId, setCommandId] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  // Handle submit and command creation
  const handleSubmit = async () => {
    if (!file) {
      alert('Please select a PDF file')
      return
    }

    try {
      setUploading(true)
      const response = await processApi.createPdfToHtmlCommand(file)
      setCommandId(response.command_id)
    } catch (err: any) {
      alert(`Failed to create command: ${err.message || 'Unknown error'}`)
    } finally {
      setUploading(false)
    }
  }

  // Handle processing completion
  const handleComplete = (commandResult: any) => {
    setResult(commandResult)
  }

  return (
    <div className="max-w-xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">PDF to HTML Summary</h1>
      <p className="text-gray-600 mb-6">Convert a PDF to an interactive HTML summary with questions and answers</p>
      
      {!commandId && (
        <div className="space-y-4">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              id="file-input"
              onChange={handleFileChange}
              disabled={uploading}
            />
            <label htmlFor="file-input" className="cursor-pointer">
              <div className="text-4xl mb-2">📄</div>
              <div className="text-gray-600">
                {file ? file.name : 'Click to select a PDF file'}
              </div>
            </label>
          </div>
          <button
            className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
            onClick={handleSubmit}
            disabled={uploading || !file}
          >
            {uploading ? 'Processing...' : 'Convert to HTML Summary'}
          </button>
        </div>
      )}

      {commandId && !result && (
        <WaitSection commandId={commandId} onComplete={handleComplete} />
      )}

      {result && (
        <DownloadSection
          fileId={result.html_file_id}
          filename={result.html_filename || 'summary.html'}
          onReset={() => {
            setResult(null)
            setCommandId(null)
            setFile(null)
          }}
          label="Download HTML Summary"
        />
      )}
    </div>
  )
}
