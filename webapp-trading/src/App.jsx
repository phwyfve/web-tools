import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import MarketMovers from './pages/MarketMovers'
import Scans from './pages/Scans'
import './App.css'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/market-movers" element={<MarketMovers />} />
          <Route path="/scans" element={<Scans />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
