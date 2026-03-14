import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardLayout from './components/layouts/DashboardLayout'
import Dashboard from './pages/Dashboard'
import SirenPage from './pages/SirenPage'
import LogementsPage from './pages/LogementsPage'
import UsagePage from './pages/UsagePage'
import RecettesPage from './pages/RecettesPage'
import DepensesPage from './pages/DepensesPage'
import EmpruntsPage from './pages/EmpruntsPage'
import OgaPage from './pages/OgaPage'
import StatutFiscalPage from './pages/StatutFiscalPage'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="siren" element={<SirenPage />} />
              <Route path="logements" element={<LogementsPage />} />
              <Route path="usage" element={<UsagePage />} />
              <Route path="recettes" element={<RecettesPage />} />
              <Route path="depenses" element={<DepensesPage />} />
              <Route path="emprunts" element={<EmpruntsPage />} />
              <Route path="oga" element={<OgaPage />} />
              <Route path="statut-fiscal" element={<StatutFiscalPage />} />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
