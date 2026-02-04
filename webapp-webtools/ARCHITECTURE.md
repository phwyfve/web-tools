# Hybrid Architecture - PDF Web Tools

## Overview

This document describes the new **hybrid architecture** implemented for the PDF processing workflows. This architecture combines the best aspects of single-page and multi-page approaches, using query parameters for state management while keeping each tool on its own route.

## Architecture Principles

### URL Structure
- Each tool has **ONE route** (e.g., `/merge-pdfs`, `/split-pdf`)
- Workflow state is tracked via **query parameters** (e.g., `?command=XXX`)
- URL stays the same throughout the workflow
- State persists across page refreshes
- Back button works intuitively

### Component Structure

#### Reusable Workflow Components
Located in `src/components/workflow/`:

1. **UploadSection.tsx** - File upload with drag-drop
   - Props: `acceptedFormats`, `multiple`, `onFilesSelected`, `onError`
   - Handles file validation and selection
   - No submit button (parent component handles that)

2. **WaitSection.tsx** - Processing status polling
   - Props: `commandId`, `onComplete`, `onError`
   - Polls backend every 2 seconds for command status
   - Shows progress indicator and status messages
   - Calls `onComplete` callback with result when done

3. **DownloadSection.tsx** - File download UI
   - Props: `fileId`, `filename`, `onReset`, `title`, `description`
   - Triggers file download
   - Offers "Process Another" button to reset workflow

#### Tool Pages
Located in `src/pages/`:

Each tool page (e.g., `MergePdf.tsx`, `SplitPdf.tsx`) follows this pattern:

```tsx
export default function ToolPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const commandId = searchParams.get('command')
  
  const [uploading, setUploading] = useState(false)
  const [files, setFiles] = useState<File[]>([])
  const [result, setResult] = useState(null)

  // Conditional rendering based on workflow state
  if (result) {
    return <DownloadSection {...props} onReset={handleReset} />
  }
  
  if (commandId) {
    return <WaitSection commandId={commandId} onComplete={handleComplete} />
  }
  
  // Default: Upload phase
  return <UploadSection {...props} onFilesSelected={handleFilesSelected} />
}
```

### Workflow States

1. **Upload Phase** (default)
   - URL: `/tool-name`
   - User selects files
   - Parent page renders `<UploadSection />`
   - Parent provides custom upload button
   - On upload: creates command, updates URL to `?command=XXX`

2. **Processing Phase**
   - URL: `/tool-name?command=XXX`
   - Page renders `<WaitSection />`
   - Polls backend for status
   - On completion: calls `onComplete` callback with result

3. **Download Phase**
   - URL: `/tool-name?command=XXX` (stays same)
   - Page renders `<DownloadSection />`
   - User downloads result file
   - "Process Another" button clears query params → back to upload

### State Management

- **Files**: Local state in tool page component
- **Command ID**: URL query parameter (`?command=XXX`)
- **Result**: Local state in tool page component
- **No** React Router navigation between phases
- **No** separate routes for upload/wait/download

### Benefits

✅ **Single URL per tool** - Clean, bookmarkable URLs
✅ **State persistence** - Refresh works, back button works
✅ **Reusable components** - UploadSection, WaitSection, DownloadSection
✅ **Scalable** - New tools only need ~50 lines of code
✅ **Type-safe** - Full TypeScript support
✅ **Minimal navigation** - No router.navigate() calls
✅ **Better UX** - Feels like a single-page app
✅ **SEO-friendly** - Each tool has dedicated route

## Implementation Examples

### MergePdf.tsx (Multi-file upload)

```tsx
<UploadSection
  acceptedFormats={['.pdf']}
  multiple={true}
  onFilesSelected={handleFilesSelected}
  onError={(error: string) => alert(error)}
/>

{files.length > 0 && (
  <button onClick={handleUpload} disabled={uploading || files.length < 2}>
    {uploading ? 'Uploading...' : `Merge ${files.length} PDFs`}
  </button>
)}
```

### SplitPdf.tsx (Single-file upload)

```tsx
<UploadSection
  acceptedFormats={['.pdf']}
  multiple={false}
  onFilesSelected={handleFilesSelected}
  onError={(error: string) => alert(error)}
/>

{file && (
  <button onClick={handleUpload} disabled={uploading}>
    {uploading ? 'Uploading...' : 'Split PDF into Pages'}
  </button>
)}
```

## Routing Configuration

### App.tsx Routes

```tsx
{/* New hybrid architecture routes */}
<Route path="/merge-pdfs" element={<ProtectedRoute><MergePdf /></ProtectedRoute>} />
<Route path="/split-pdf" element={<ProtectedRoute><SplitPdf /></ProtectedRoute>} />

{/* Legacy routes (backward compatibility) */}
<Route path="/upload/:category/:tool" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
<Route path="/wait/:processId" element={<ProtectedRoute><Wait /></ProtectedRoute>} />
<Route path="/download/:processId" element={<ProtectedRoute><Download /></ProtectedRoute>} />
```

### Home.tsx Navigation

```tsx
// Map specific tools to their hybrid routes
if (category.id === 'merge' && tool.id === 'merge-pdf') {
  toolPath = '/merge-pdfs'
} else if (category.id === 'split' && tool.id === 'split-pdf') {
  toolPath = '/split-pdf'
}
```

## Adding a New Tool

To add a new PDF processing tool (e.g., Compress PDF):

1. **Create backend route** (e.g., `routes/compress_pdf.py`)
2. **Create backend command** (e.g., `tools_commands/CompressPdf.py`)
3. **Add API method** in `services/api.ts`:
   ```tsx
   createCompressPdfCommand: async (file: File) => {
     const formData = new FormData()
     formData.append('file', file)
     const response = await api.post('/api/compressPdf', formData, {
       headers: { 'Content-Type': 'multipart/form-data' }
     })
     return response.data
   }
   ```

4. **Create tool page** (`pages/CompressPdf.tsx`):
   ```tsx
   import { useState } from 'react'
   import { useSearchParams } from 'react-router-dom'
   import UploadSection from '../components/workflow/UploadSection'
   import WaitSection from '../components/workflow/WaitSection'
   import DownloadSection from '../components/workflow/DownloadSection'
   import { processApi } from '../services/api'

   export default function CompressPdf() {
     const [searchParams, setSearchParams] = useSearchParams()
     const commandId = searchParams.get('command')
     
     const [uploading, setUploading] = useState(false)
     const [file, setFile] = useState<File | null>(null)
     const [result, setResult] = useState(null)

     const handleFilesSelected = (selectedFiles: File[]) => {
       setFile(selectedFiles[0])
     }

     const handleUpload = async () => {
       if (!file) return
       try {
         setUploading(true)
         const response = await processApi.createCompressPdfCommand(file)
         setSearchParams({ command: response.command_id })
       } catch (err: any) {
         alert(`Upload failed: ${err.message}`)
       } finally {
         setUploading(false)
       }
     }

     const handleComplete = (commandResult: any) => {
       setResult(commandResult)
     }

     const handleReset = () => {
       setSearchParams({})
       setFile(null)
       setResult(null)
     }

     if (result) {
       return (
         <DownloadSection
           fileId={result.compressed_file_id}
           filename="compressed.pdf"
           onReset={handleReset}
           title="Your PDF has been compressed!"
         />
       )
     }

     if (commandId) {
       return (
         <WaitSection
           commandId={commandId}
           onComplete={handleComplete}
           onError={(error) => { alert(error); handleReset() }}
         />
       )
     }

     return (
       <div className="max-w-4xl mx-auto py-12 px-4">
         <div className="bg-white rounded-lg shadow-lg p-8">
           <h1 className="text-3xl font-bold mb-2">Compress PDF</h1>
           <p className="text-gray-600 mb-8">Reduce PDF file size</p>
           
           <UploadSection
             acceptedFormats={['.pdf']}
             multiple={false}
             onFilesSelected={handleFilesSelected}
             onError={(error: string) => alert(error)}
           />

           {file && (
             <button onClick={handleUpload} disabled={uploading}>
               {uploading ? 'Uploading...' : 'Compress PDF'}
             </button>
           )}
         </div>
       </div>
     )
   }
   ```

5. **Add route** in `App.tsx`:
   ```tsx
   <Route path="/compress-pdf" element={<ProtectedRoute><CompressPdf /></ProtectedRoute>} />
   ```

6. **Add to tools config** in `config/tools.ts`

7. **Update Home.tsx** navigation logic if needed

## File Structure

```
webapp-webtools/
├── src/
│   ├── components/
│   │   └── workflow/
│   │       ├── UploadSection.tsx     # Reusable upload component
│   │       ├── WaitSection.tsx       # Reusable polling component
│   │       └── DownloadSection.tsx   # Reusable download component
│   ├── pages/
│   │   ├── Home.tsx                  # Tool category listing
│   │   ├── MergePdf.tsx              # Hybrid: Merge PDFs workflow
│   │   ├── SplitPdf.tsx              # Hybrid: Split PDF workflow
│   │   ├── Upload.tsx                # Legacy: Generic upload page
│   │   ├── Wait.tsx                  # Legacy: Generic waiting page
│   │   └── Download.tsx              # Legacy: Generic download page
│   ├── services/
│   │   └── api.ts                    # API client with command methods
│   ├── config/
│   │   └── tools.ts                  # Tool metadata configuration
│   └── App.tsx                       # Route definitions
```

## Migration Strategy

### Phase 1: ✅ Completed
- Created reusable workflow components
- Refactored MergePdf.tsx to hybrid architecture
- Refactored SplitPdf.tsx to hybrid architecture
- Added new routes in App.tsx
- Updated Home.tsx navigation

### Phase 2: Future Work
- Migrate other existing tools to hybrid architecture
- Deprecate legacy Upload/Wait/Download routes
- Remove backward compatibility once migration complete
- Update documentation and examples

### Phase 3: Optimization
- Add loading skeletons
- Add error boundaries
- Implement retry logic
- Add progress percentage from backend
- Cache results temporarily

## Comparison with Other Approaches

### Three-Page Architecture (Legacy)
- ❌ Separate routes: `/upload`, `/wait/:id`, `/download/:id`
- ❌ Navigation between routes
- ❌ State lost on refresh
- ✅ Clear separation of concerns
- ✅ Works with existing backend

### Monolithic Single-Page (Previous SplitPdf)
- ✅ One component, one route
- ❌ No URL state persistence
- ❌ State lost on refresh
- ❌ Back button doesn't work
- ❌ Hard to maintain (250+ lines)

### Hybrid Architecture (Current) ⭐
- ✅ One route per tool
- ✅ Query params for state
- ✅ State persists on refresh
- ✅ Back button works
- ✅ Reusable components
- ✅ Scalable and maintainable
- ✅ Clean URLs

## Testing Checklist

For each tool page:

- [ ] Upload files → URL updates with `?command=XXX`
- [ ] Refresh during upload → Returns to upload phase (expected)
- [ ] Refresh during processing → Continues polling (works!)
- [ ] Refresh during download → Shows download section (works!)
- [ ] Back button during processing → Returns to upload
- [ ] "Process Another" → Clears query params
- [ ] Multiple file validation (merge only)
- [ ] Single file validation (split/compress)
- [ ] File format validation
- [ ] Error handling (network errors)
- [ ] Error handling (processing failures)

## Performance Considerations

- Polling interval: 2 seconds (configurable)
- File size limits: Set in backend
- Memory: Files held in state until reset
- Network: Efficient polling, stops when done

## Security Considerations

- File validation on both frontend and backend
- Authentication required (ProtectedRoute)
- GridFS for temporary file storage
- Command IDs are MongoDB ObjectIds (not guessable)

## Conclusion

The hybrid architecture provides:
- **Better UX** than separate-route approach
- **Better maintainability** than monolithic approach
- **Scalability** for adding new tools
- **Type safety** with TypeScript
- **State persistence** with query params

This is the recommended pattern for all future PDF processing tools.
