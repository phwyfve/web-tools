import { Link, useLocation } from 'react-router-dom'
import './Layout.css'

function Layout({ children }) {
  const location = useLocation()

  return (
    <div className="layout">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h2>Market Analysis</h2>
        </div>
        <ul className="sidebar-nav">
          <li className={location.pathname === '/' ? 'active' : ''}>
            <Link to="/">
              <span className="icon">🏠</span>
              Home
            </Link>
          </li>
          <li className={location.pathname === '/stocks' ? 'active' : ''}>
            <Link to="/stocks">
              <span className="icon">📊</span>
              Stocks
            </Link>
          </li>
          <li className={location.pathname === '/market-movers' ? 'active' : ''}>
            <Link to="/market-movers">
              <span className="icon">📈</span>
              Market Movers
            </Link>
          </li>
          <li className={location.pathname === '/scans' ? 'active' : ''}>
            <Link to="/scans">
              <span className="icon">🔍</span>
              Scans
            </Link>
          </li>
        </ul>
      </nav>
      <main className="main-content">
        <header className="top-header">
          <div className="search-bar">
            <span className="search-icon">🔍</span>
            <input type="text" placeholder="Company or stock symbol..." />
          </div>
          <div className="user-actions">
            <button className="btn-secondary">Log In</button>
            <button className="btn-primary">Sign Up</button>
          </div>
        </header>
        <div className="content">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout
