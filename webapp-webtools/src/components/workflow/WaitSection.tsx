import { useEffect, useState } from 'react'
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { processApi, type CommandStatus } from '../../services/api'

interface WaitSectionProps {
  commandId: string
  onComplete: (result: any) => void
  onError?: (error: string) => void
}

export default function WaitSection({ commandId, onComplete, onError }: WaitSectionProps) {
  const [status, setStatus] = useState<string>('Initializing...')
  const [commandStatus, setCommandStatus] = useState<CommandStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let pollInterval: number

    const pollStatus = async () => {
      try {
        console.log('🔄 Polling command status:', commandId)
        const response = await processApi.getCommandStatus(commandId)
        console.log('📥 Command status:', response)
        
        setCommandStatus(response)

        // Check status
        if (response.exit_state === -1) {
          // Still processing
          setStatus('Processing your files...')
        } else if (response.exit_state === 0) {
          // Success!
          setStatus('Processing complete!')
          
          // Parse result from stdout
          try {
            if (response.stdout) {
              const result = JSON.parse(response.stdout)
              console.log('✅ Processing completed:', result)
              
              // Wait a moment before calling onComplete
              setTimeout(() => {
                onComplete(result)
              }, 1000)
            } else {
              throw new Error('No result in stdout')
            }
          } catch (parseError) {
            console.error('❌ Failed to parse result:', parseError)
            const errorMsg = 'Processing completed but result is invalid'
            setError(errorMsg)
            onError?.(errorMsg)
          }
          
          // Stop polling
          clearInterval(pollInterval)
        } else {
          // Failed
          const errorMsg = response.stderr || 'Processing failed'
          console.error('❌ Processing failed:', errorMsg)
          setError(errorMsg)
          onError?.(errorMsg)
          clearInterval(pollInterval)
        }
      } catch (err: any) {
        console.error('❌ Polling error:', err)
        const errorMsg = err.message || 'Network error'
        setError(errorMsg)
        onError?.(errorMsg)
        clearInterval(pollInterval)
      }
    }

    // Initial poll
    pollStatus()

    // Poll every 2 seconds
    pollInterval = setInterval(pollStatus, 2000)

    return () => {
      clearInterval(pollInterval)
    }
  }, [commandId, onComplete, onError])

  if (error) {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <AlertCircle className="mx-auto h-16 w-16 text-red-500 mb-6" />
          <h2 className="text-2xl font-bold text-red-600 mb-4">Processing Failed</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <p className="text-xs text-gray-500">Command ID: {commandId}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto py-12">
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        {commandStatus?.exit_state === 0 ? (
          <CheckCircle className="mx-auto h-16 w-16 text-green-500 mb-6" />
        ) : (
          <Loader2 className="mx-auto h-16 w-16 text-blue-600 animate-spin mb-6" />
        )}
        
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          {commandStatus?.exit_state === 0 ? 'Processing Complete!' : 'Processing...'}
        </h2>
        
        <p className="text-gray-600 mb-6">{status}</p>

        {/* Progress indicator */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
            style={{ width: commandStatus?.exit_state === 0 ? '100%' : '50%' }}
          ></div>
        </div>

        <p className="text-xs text-gray-500">Command ID: {commandId}</p>
        
        {commandStatus && (
          <div className="mt-4 text-xs text-left bg-gray-50 p-4 rounded-lg">
            <p className="font-mono text-gray-700">
              <span className="font-semibold">Command:</span> {commandStatus.shell_command}
            </p>
            <p className="font-mono text-gray-700 mt-1">
              <span className="font-semibold">Status:</span>{' '}
              {commandStatus.exit_state === -1 ? 'Running' : 
               commandStatus.exit_state === 0 ? 'Success' : 'Failed'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
