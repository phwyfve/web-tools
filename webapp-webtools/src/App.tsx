import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ToastProvider } from './contexts/ToastContext'
import Layout from './components/Layout'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Upload from './pages/Upload'
import Wait from './pages/Wait'
import Download from './pages/Download'
import SplitPdf from './pages/SplitPdf'
import MergePdf from './pages/MergePdf'
import MergeImages from './pages/MergeImages'
import YoutubeSummary from './pages/YoutubeSummary'
import XlsToPdf from './pages/XlsToPdf'
import ProtectedRoute from './components/ProtectedRoute'


function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Layout>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>
            } />
            
            {/* New hybrid architecture routes */}
            <Route path="/merge-pdfs" element={
              <ProtectedRoute>
                <MergePdf />
              </ProtectedRoute>
            } />
            <Route path="/merge-images" element={
              <ProtectedRoute>
                <MergeImages />
              </ProtectedRoute>
            } />
            <Route path="/excel-to-pdf" element={
              <ProtectedRoute>
                <XlsToPdf />
              </ProtectedRoute>
            } />
            <Route path="/split-pdf" element={
              <ProtectedRoute>
                <SplitPdf />
              </ProtectedRoute>
            } />
            <Route path="/youtube-summary" element={
              <ProtectedRoute>
                <YoutubeSummary />
              </ProtectedRoute>
            } />

            {/* Legacy routes (for backward compatibility) */}
            <Route path="/upload/:category/:tool" element={
              <ProtectedRoute>
                <Upload />
              </ProtectedRoute>
            } />
            <Route path="/split/split-pdf" element={
              <ProtectedRoute>
                <SplitPdf />
              </ProtectedRoute>
            } />
            <Route path="/wait/:processId" element={
              <ProtectedRoute>
                <Wait />
              </ProtectedRoute>
            } />
            <Route path="/download/:processId" element={
              <ProtectedRoute>
                <Download />
              </ProtectedRoute>
            } />
          </Routes>
        </Layout>
      </ToastProvider>
    </AuthProvider>
  )
}

export default App
