import { useState, useEffect } from 'react'
import StockTable from '../components/StockTable'
import { fetchLeaderboard } from '../services/tradingApi'
import './MarketMovers.css'

function MarketMovers() {
  const [activeTab, setActiveTab] = useState('gainers')
  const [activePeriod, setActivePeriod] = useState('5d')
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [pageStart, setPageStart] = useState(0)
  const [pageLimit, setPageLimit] = useState(20)
  const [totalItems, setTotalItems] = useState(0)

  const tabs = [
    { id: 'gainers', label: 'Gainers' },
    { id: 'losers', label: 'Losers' },
    { id: 'active', label: 'Most Active' },
  ]

  const periods = [
    { id: '5d', label: '5D' },
    { id: '1M', label: '1M' },
    { id: '2M', label: '2M' },
    { id: '3M', label: '3M' },
    { id: '6M', label: '6M' },
    { id: '52w', label: '52W' },
  ]

  const getLeaderboardType = (tab) => {
    if (tab === 'gainers') return 'high'
    if (tab === 'losers') return 'low'
    if (tab === 'active') return 'volume'
    return 'high'
  }

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError(null)
      try {
        const leaderboardType = getLeaderboardType(activeTab)
        const period = activeTab === 'active' ? 'market_movers' : activePeriod
        const result = await fetchLeaderboard(period, leaderboardType, pageStart, pageLimit)
        
        console.log('Leaderboard API result:', result)
        
        // Backend now returns a single leaderboard with items (or empty object)
        const transformedData = result.items
          ? result.items.map(item => ({
              symbol: item.symbol || item.instrumentId.split(':')[1] || item.instrumentId,
              companyName: item.symbol || item.instrumentId,
              changePercent: item.change_pct || 0,
              stockPrice: item.last_price || 0,
              volume: item.volume || 0,
              marketCap: item.market_cap || 0,
            }))
          : []
        
        console.log('Transformed data:', transformedData)
        
        setData(transformedData)
        setTotalItems(result.total || 0)
      } catch (err) {
        setError(err.message)
        console.error('Failed to load data:', err)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [activeTab, activePeriod, pageStart, pageLimit])

  const handlePreviousPage = () => {
    setPageStart(prev => Math.max(0, prev - pageLimit))
  }

  const handleNextPage = () => {
    if (pageStart + pageLimit < totalItems) {
      setPageStart(prev => prev + pageLimit)
    }
  }

  const handlePageSizeChange = (e) => {
    setPageLimit(Number(e.target.value))
    setPageStart(0) // Reset to first page when changing page size
  }

  const currentPage = Math.floor(pageStart / pageLimit) + 1
  const totalPages = Math.ceil(totalItems / pageLimit)

  return (
    <div className="market-movers">
      <h1 className="page-title">Market Movers</h1>
      
      <div className="tabs-container">
        <div className="tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        
        <div className="full-width-toggle">
          <span>Full Width</span>
          <input type="checkbox" />
        </div>
      </div>

      {activeTab !== 'active' && (
        <div className="periods">
          {periods.map(period => (
            <button
              key={period.id}
              className={`period-btn ${activePeriod === period.id ? 'active' : ''}`}
              onClick={() => setActivePeriod(period.id)}
            >
              {period.label}
            </button>
          ))}
        </div>
      )}

      <div className="table-header">
        <h2>
          {activeTab === 'gainers' ? 'Gainers' : activeTab === 'losers' ? 'Losers' : 'Most Active'}{' '}
          {activeTab !== 'active' ? periods.find(p => p.id === activePeriod)?.label : ''}
        </h2>
        <span className="update-time">
          Updated {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
        </span>
      </div>

      {loading && <div className="loading">Loading...</div>}
      {error && <div className="error">Error: {error}</div>}
      {!loading && !error && (
        <>
          <StockTable data={data} pageStart={pageStart} />
          
          <div className="pagination-container">
            <div className="pagination-info">
              Page {currentPage} of {totalPages} | {totalItems} total items
            </div>
            
            <div className="pagination-controls">
              <button 
                onClick={handlePreviousPage} 
                disabled={pageStart === 0}
                className="pagination-btn"
              >
                &lt; Previous
              </button>
              
              <select 
                value={pageLimit} 
                onChange={handlePageSizeChange}
                className="page-size-select"
              >
                <option value={20}>20 Rows</option>
                <option value={50}>50 Rows</option>
                <option value={100}>100 Rows</option>
              </select>
              
              <button 
                onClick={handleNextPage} 
                disabled={pageStart + pageLimit >= totalItems}
                className="pagination-btn"
              >
                Next &gt;
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default MarketMovers
