import { API_ENDPOINTS } from '../config/api'

export const fetchLeaderboard = async (period, type = 'high', start = 0, limit = 20) => {
  try {
    const response = await fetch(API_ENDPOINTS.TRADING_DATA, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        data_type: 'leaderboard',
        period: period,
        leaderboard_type: type,
        start: start,
        limit: limit,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data.result || []
  } catch (error) {
    console.error('Error fetching leaderboard:', error)
    throw error
  }
}

export const fetchStock = async (symbol, period = null) => {
  try {
    const response = await fetch(API_ENDPOINTS.TRADING_DATA, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        data_type: 'stock',
        symbol: symbol,
        period: period,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data.result || []
  } catch (error) {
    console.error('Error fetching stock:', error)
    throw error
  }
}

export const fetchNamedQuery = async (namedQuery, start = 0, limit = 500) => {
  try {
    const response = await fetch(API_ENDPOINTS.NAMED_QUERY, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        named_query: namedQuery,
        start: start,
        limit: limit,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data.result || { items: [], total: 0 }
  } catch (error) {
    console.error('Error fetching named query:', error)
    throw error
  }
}
