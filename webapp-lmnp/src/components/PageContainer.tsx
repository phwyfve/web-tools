import { ReactNode } from 'react'

interface PageContainerProps {
  title: string
  children: ReactNode
}

export default function PageContainer({ title, children }: PageContainerProps) {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">{title}</h1>
        {children}
      </div>
    </div>
  )
}
