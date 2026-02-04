import { useState } from 'react'
import WaitSection from '../components/workflow/WaitSection'
import DownloadSection from '../components/workflow/DownloadSection'
import { processApi } from '../services/api'

export default function YoutubeSummary() {
  const [url, setUrl] = useState('')
  const [commandId, setCommandId] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)

  // Handle URL input
  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value)
  }

  // Handle submit and command creation
  const handleSubmit = async () => {
    if (!url) {
      alert('Please enter a YouTube video URL')
      return
    }
    try {
      setUploading(true)
      const response = await processApi.createYoutubeSummaryCommand(url)
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
      <h1 className="text-2xl font-bold mb-4">YouTube Video Summary</h1>
      {!commandId && (
        <div className="space-y-4">
          <input
            type="text"
            className="w-full border rounded px-3 py-2"
            placeholder="Paste YouTube video URL here..."
            value={url}
            onChange={handleUrlChange}
            disabled={uploading}
          />
          <button
            className="bg-pink-600 text-white px-4 py-2 rounded hover:bg-pink-700"
            onClick={handleSubmit}
            disabled={uploading}
          >
            {uploading ? 'Processing...' : 'Summarize Video'}
          </button>
        </div>
      )}
      {commandId && !result && (
        <WaitSection commandId={commandId} onComplete={handleComplete} />
      )}
      {result && (
        <DownloadSection
          fileId={result.summary_file_id}
          filename={result.summary_filename || 'output.html'}
          label="Download Summary (HTML)"
        />
      )}
    </div>
  )
}
