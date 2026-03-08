import { useState } from 'react'
import WaitSection from '../components/workflow/WaitSection'
import DownloadSection from '../components/workflow/DownloadSection'
import { processApi } from '../services/api'

export default function HtmlSummary() {
  const [content, setContent] = useState('')
  const [title, setTitle] = useState('')
  const [commandId, setCommandId] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState<any>(null)

  // Handle content input
  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value)
  }

  // Handle title input
  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTitle(e.target.value)
  }

  // Handle submit and command creation
  const handleSubmit = async () => {
    if (!content.trim()) {
      alert('Please enter some content to summarize')
      return
    }

    try {
      setProcessing(true)
      const response = await processApi.createHtmlSummaryCommand(content, title)
      setCommandId(response.command_id)
    } catch (err: any) {
      alert(`Failed to create command: ${err.message || 'Unknown error'}`)
    } finally {
      setProcessing(false)
    }
  }

  // Handle processing completion
  const handleComplete = (commandResult: any) => {
    setResult(commandResult)
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">HTML Summary Generator</h1>
      <p className="text-gray-600 mb-6">Create a quick HTML summary with 1 main question and 5 subquestions</p>

      {!commandId && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Title (optional)
            </label>
            <input
              type="text"
              className="w-full border rounded px-3 py-2"
              placeholder="Enter a title for this summary..."
              value={title}
              onChange={handleTitleChange}
              disabled={processing}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content to Summarize *
            </label>
            <textarea
              className="w-full border rounded px-3 py-2 h-64"
              placeholder="Paste your text content here..."
              value={content}
              onChange={handleContentChange}
              disabled={processing}
            />
            <div className="text-sm text-gray-500 mt-1">
              {content.length} characters
            </div>
          </div>

          <button
            className="w-full bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:bg-gray-400"
            onClick={handleSubmit}
            disabled={processing || !content.trim()}
          >
            {processing ? 'Creating Summary...' : 'Generate HTML Summary'}
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
            setContent('')
            setTitle('')
          }}
          label="Download HTML Summary"
        />
      )}
    </div>
  )
}
