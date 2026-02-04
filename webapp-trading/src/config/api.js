export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const API_ENDPOINTS = {
  TRADING_DATA: `${API_BASE_URL}/api/trading/data`,
  NAMED_QUERY: `${API_BASE_URL}/api/trading/named_query`,
}
