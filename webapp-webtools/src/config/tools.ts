export interface Tool {
  id: string
  name: string
  description: string
  acceptedFormats: string[]
  icon: string
  color: string
}

export interface Category {
  id: string
  name: string
  description: string
  color: string
  borderColor: string
  bgColor: string
  tools: Tool[]
}

export const categories: Category[] = [
  {
    id: 'merge',
    name: 'Merge',
    description: 'Combine multiple files into one',
    color: 'text-blue-700',
    borderColor: 'border-blue-500',
    bgColor: 'bg-blue-50 hover:bg-blue-100',
    tools: [
      {
        id: 'merge-pdf',
        name: 'Merge PDFs',
        description: 'Combine multiple PDF files into a single document',
        acceptedFormats: ['.pdf'],
        icon: '📄',
        color: 'text-blue-600',
      },
      {
        id: 'merge-images',
        name: 'Merge Images to PDF',
        description: 'Combine multiple images into one PDF',
        acceptedFormats: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        icon: '🖼️',
        color: 'text-blue-600',
      },
    ],
  },
  {
    id: 'split',
    name: 'Split',
    description: 'Split files into multiple parts',
    color: 'text-purple-700',
    borderColor: 'border-purple-500',
    bgColor: 'bg-purple-50 hover:bg-purple-100',
    tools: [
      {
        id: 'split-pdf',
        name: 'Split PDF',
        description: 'Split a PDF file into individual pages',
        acceptedFormats: ['.pdf'],
        icon: '✂️',
        color: 'text-purple-600',
      },
    ],
  },
  {
    id: 'convert',
    name: 'Convert to PDF',
    description: 'Convert various file formats to PDF',
    color: 'text-green-700',
    borderColor: 'border-green-500',
    bgColor: 'bg-green-50 hover:bg-green-100',
    tools: [
      {
        id: 'excel-to-pdf',
        name: 'Excel to PDF',
        description: 'Convert Excel spreadsheets to PDF',
        acceptedFormats: ['.xlsx', '.xls'],
        icon: '📊',
        color: 'text-green-600',
      },
      {
        id: 'image-to-pdf',
        name: 'Images to PDF',
        description: 'Convert images to PDF format',
        acceptedFormats: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
        icon: '🖼️',
        color: 'text-green-600',
      },
    ],
  },
  ,
  {
    id: 'ai-agents',
    name: 'AI Agents',
    description: 'AI-powered automation and analysis tools',
    color: 'text-pink-700',
    borderColor: 'border-pink-500',
    bgColor: 'bg-pink-50 hover:bg-pink-100',
    tools: [
      {
        id: 'youtube-summary',
        name: 'YouTube Video Summary',
        description: 'Summarize a YouTube video and download the result as HTML',
        acceptedFormats: ['url'],
        icon: '🎬',
        color: 'text-pink-600',
      },
    ],
  }
]

export const getCategoryById = (id: string): Category | undefined => {
  return categories.find(category => category.id === id)
}

export const getToolById = (categoryId: string, toolId: string): Tool | undefined => {
  const category = getCategoryById(categoryId)
  return category?.tools.find(tool => tool.id === toolId)
}
