import { useState, useEffect } from 'react'
import { fetchNamedQuery } from '../services/tradingApi'
import './Scans.css'

function Scans() {
  const [selectedScan, setSelectedScan] = useState(null)
  const [scanResults, setScanResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [pageStart, setPageStart] = useState(0)
  const [pageLimit, setPageLimit] = useState(500)

  const scans = {
    bullish: [
      {
        id: 'strong_uptrends',
        name: 'Strong Uptrends To New Highs',
        disabled: true
      },
      {
        id: 'strong_volume_gainers',
        name: 'Strong Volume Gainers',
        disabled: true
      },
      {
        id: 'moving_average_correct_order',
        name: 'Moving Averages In Correct Order',
        disabled: false,
        namedQuery: 'moving_average_correct_order'
      },
      {
        id: 'bullish_ma_crossovers',
        name: 'Bullish 50/200-day MA Crossovers',
        disabled: true
      },
      {
        id: 'bullish_macd_crossovers',
        name: 'Bullish MACD Crossovers',
        disabled: true
      },
      {
        id: 'oversold_improving_rsi',
        name: 'Oversold with an Improving RSI',
        disabled: true
      },
      {
        id: 'above_upper_bollinger',
        name: 'Moved Above Upper Bollinger Band',
        disabled: true
      }
    ],
    bearish: [
      {
        id: 'strong_downtrends',
        name: 'Strong Downtrends To New Lows',
        disabled: true
      },
      {
        id: 'strong_volume_decliners',
        name: 'Strong Volume Decliners',
        disabled: true
      },
      {
        id: 'moving_average_wrong_order',
        name: 'Moving Averages In Wrong Order',
        disabled: true
      },
      {
        id: 'bearish_ma_crossovers',
        name: 'Bearish 50/200-day MA Crossovers',
        disabled: true
      },
      {
        id: 'bearish_macd_crossovers',
        name: 'Bearish MACD Crossovers',
        disabled: true
      },
      {
        id: 'overbought_declining_rsi',
        name: 'Overbought with a Declining RSI',
        disabled: true
      },
      {
        id: 'below_lower_bollinger',
        name: 'Moved Below Lower Bollinger Band',
        disabled: true
      }
    ]
  }

  const handleRunScan = async (scan) => {
    if (scan.disabled) return
    
    setSelectedScan(scan)
    setLoading(true)
    setError(null)
    setScanResults(null)
    setPageStart(0)

    try {
      const result = await fetchNamedQuery(scan.namedQuery, pageStart, pageLimit)
      setScanResults(result)
    } catch (err) {
      setError(err.message)
      console.error('Failed to run scan:', err)
    } finally {
      setLoading(false)
    }
  }

  const handlePreviousPage = async () => {
    const newStart = Math.max(0, pageStart - pageLimit)
    setPageStart(newStart)
    await loadPage(newStart)
  }

  const handleNextPage = async () => {
    if (pageStart + pageLimit < scanResults.total) {
      const newStart = pageStart + pageLimit
      setPageStart(newStart)
      await loadPage(newStart)
    }
  }

  const loadPage = async (start) => {
    if (!selectedScan) return
    
    setLoading(true)
    setError(null)

    try {
      const result = await fetchNamedQuery(selectedScan.namedQuery, start, pageLimit)
      setScanResults(result)
    } catch (err) {
      setError(err.message)
      console.error('Failed to load page:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatNumber = (num) => {
    if (!num) return '0'
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B'
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M'
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K'
    return num.toLocaleString()
  }

  const formatPrice = (price) => {
    if (!price) return '0.00'
    return parseFloat(price).toFixed(3)
  }

  const formatPercent = (percent) => {
    if (percent === null || percent === undefined) return '0.0'
    return parseFloat(percent).toFixed(1)
  }

  const currentPage = Math.floor(pageStart / pageLimit) + 1
  const totalPages = Math.ceil((scanResults?.total || 0) / pageLimit)

  if (scanResults) {
    return (
      <div className="scans-results">
        <div className="results-header">
          <button className="back-btn" onClick={() => setScanResults(null)}>
            ← Back to Scans
          </button>
          <h1>{selectedScan.name}</h1>
        </div>

        <div className="results-info">
          <div className="tabs">
            <button className="tab active">Summary</button>
            <button className="tab">SharpCharts</button>
            <button className="tab">CandleGlance</button>
          </div>
          <div className="matching-results">
            Matching Results: <strong>{scanResults.total || 0}</strong>
          </div>
        </div>

        {loading && <div className="loading">Loading...</div>}
        {error && <div className="error">Error: {error}</div>}
        
        {!loading && !error && scanResults.items && (
          <>
            <div className="results-table-container">
              <table className="results-table">
                <thead>
                  <tr>
                    <th></th>
                    <th>SYMBOL</th>
                    <th>NAME</th>
                    <th>LAST</th>
                    <th>VOLUME</th>
                    <th>SCTR</th>
                    <th>5d CHG%</th>
                  </tr>
                </thead>
                <tbody>
                  {scanResults.items.map((item, index) => (
                    <tr key={item.instrumentId || index}>
                      <td>
                        <input type="checkbox" />
                      </td>
                      <td className="symbol">
                        <a href={`/stocks/${item.symbol}`}>{item.symbol}</a>
                      </td>
                      <td className="name">{item.name || item.symbol}</td>
                      <td className="price">{formatPrice(item.last_price)}</td>
                      <td className="volume">{formatNumber(item.volume)}</td>
                      <td className="sctr">-</td>
                      <td className={`change ${item.change_pct_from_low_5d >= 0 ? 'positive' : 'negative'}`}>
                        {formatPercent(item.change_pct_from_low_5d)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pagination-container">
              <div className="pagination-info">
                Page {currentPage} of {totalPages}
              </div>
              
              <div className="pagination-controls">
                <button 
                  onClick={handlePreviousPage} 
                  disabled={pageStart === 0}
                  className="pagination-btn"
                >
                  &lt; Previous
                </button>
                
                <span className="page-info">
                  {pageStart + 1} - {Math.min(pageStart + pageLimit, scanResults.total)} of {scanResults.total}
                </span>
                
                <button 
                  onClick={handleNextPage} 
                  disabled={pageStart + pageLimit >= scanResults.total}
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

  return (
    <div className="scans">
      <h1 className="page-title">Predefined Scans</h1>

      <div className="scans-grid">
        <div className="scans-section">
          <h2 className="section-title bullish">
            <span className="icon">↑</span> Popular Bullish Scans
          </h2>
          <div className="scan-list">
            {scans.bullish.map(scan => (
              <div key={scan.id} className="scan-item">
                <span className="scan-name">{scan.name}</span>
                <div className="scan-actions">
                  <button 
                    className="btn-run" 
                    onClick={() => handleRunScan(scan)}
                    disabled={scan.disabled}
                  >
                    <span className="icon">▶</span> Run
                  </button>
                  <button className="btn-edit" disabled>
                    <span className="icon">✎</span> Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="scans-section">
          <h2 className="section-title bearish">
            <span className="icon">↓</span> Popular Bearish Scans
          </h2>
          <div className="scan-list">
            {scans.bearish.map(scan => (
              <div key={scan.id} className="scan-item">
                <span className="scan-name">{scan.name}</span>
                <div className="scan-actions">
                  <button 
                    className="btn-run" 
                    onClick={() => handleRunScan(scan)}
                    disabled={scan.disabled}
                  >
                    <span className="icon">▶</span> Run
                  </button>
                  <button className="btn-edit" disabled>
                    <span className="icon">✎</span> Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Scans
