import './StockTable.css'

function StockTable({ data, pageStart = 0 }) {
  const formatNumber = (num) => {
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B'
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M'
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K'
    return num.toLocaleString()
  }

  const formatPrice = (price) => {
    return price.toFixed(2)
  }

  const formatPercent = (percent) => {
    const sign = percent >= 0 ? '+' : ''
    return `${sign}${percent.toFixed(2)}%`
  }

  return (
    <div className="stock-table-container">
      <table className="stock-table">
        <thead>
          <tr>
            <th>No.</th>
            <th>Symbol</th>
            <th>Company Name</th>
            <th className="sortable">% Change ▼</th>
            <th>Stock Price</th>
            <th>Volume</th>
            <th>Market Cap</th>
          </tr>
        </thead>
        <tbody>
          {data.map((stock, index) => (
            <tr key={stock.symbol}>
              <td>{pageStart + index + 1}</td>
              <td className="symbol">
                <a href={`/stocks/${stock.symbol}`}>{stock.symbol}</a>
              </td>
              <td className="company-name">{stock.companyName}</td>
              <td className={`change ${stock.changePercent >= 0 ? 'positive' : 'negative'}`}>
                {formatPercent(stock.changePercent)}
              </td>
              <td className="price">{formatPrice(stock.stockPrice)}</td>
              <td className="volume">{formatNumber(stock.volume)}</td>
              <td className="market-cap">{formatNumber(stock.marketCap)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default StockTable
