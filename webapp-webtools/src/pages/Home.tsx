import { Link } from 'react-router-dom'
import { categories } from '../config/tools'
import { useAuth } from '../contexts/AuthContext'

export default function Home() {
  const { user } = useAuth()

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {user?.first_name}!
        </h1>
        <p className="text-gray-600">
          Choose a category below to start working with your files.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {categories.map((category) => (
          <div key={category.id} id={category.id} className="card">
            <div className={`border-l-4 ${category.borderColor} pl-4 mb-6`}>
              <h2 className={`text-2xl font-bold ${category.color}`}>
                {category.name}
              </h2>
              <p className="text-gray-600 mt-1">
                {category.description}
              </p>
            </div>

            <div className="grid gap-4">
              {category.tools.map((tool) => {
                // New hybrid architecture routes
                let toolPath = `/upload/${category.id}/${tool.id}` // Default legacy path

                // Map specific tools to their hybrid routes
                if (category.id === 'merge' && tool.id === 'merge-pdf') {
                  toolPath = '/merge-pdfs'
                } else if (category.id === 'merge' && tool.id === 'merge-images') {
                  toolPath = '/merge-images'
                } else if (category.id === 'convert' && tool.id === 'image-to-pdf') {
                  toolPath = '/merge-images'  // Same functionality as merge-images
                } else if (category.id === 'convert' && tool.id === 'excel-to-pdf') {
                  toolPath = '/excel-to-pdf'
                } else if (category.id === 'split' && tool.id === 'split-pdf') {
                  toolPath = '/split-pdf'
                } else if (category.id === 'ai-agents' && tool.id === 'youtube-summary') {
                  toolPath = '/youtube-summary'
                }
                
                return (
                  <Link
                    key={tool.id}
                    to={toolPath}
                    className={`block p-4 rounded-lg border-2 border-transparent ${category.bgColor} transition-all hover:border-gray-300`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">{tool.icon}</div>
                      <div className="flex-1">
                        <h3 className={`font-semibold ${tool.color}`}>
                          {tool.name}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          {tool.description}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Formats: {tool.acceptedFormats.join(', ')}
                        </p>
                      </div>
                      <div className="text-gray-400">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
