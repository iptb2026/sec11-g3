import axios from 'axios'

function isMobileContext () {
  if (typeof window === 'undefined') return false
  if (window.Capacitor?.isNativePlatform?.()) return true
  if (window.location.protocol === 'file:' || window.location.protocol === 'capacitor:') return true
  if (window.location.hostname === '10.0.2.2') return true
  if (/Android|wv|Mobile/i.test(navigator.userAgent) && window.location.port !== '9000') return true
  if (window.location.hostname === 'localhost' && !window.location.port) return true
  return false
}

function getBaseUrl () {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('bank_api_base_url')
    if (saved) return saved
  }

  const envUrl = import.meta.env.QCLI_API_BASE_URL
  if (envUrl && envUrl.startsWith('http')) {
    return envUrl
  }

  if (isMobileContext()) {
    return 'http://10.0.2.2:5000/mendoza'
  }

  return envUrl || '/mendoza'
}

const api = axios.create({
  baseURL: getBaseUrl(),
})

// If 10.0.2.2 fails or 127.0.0.1 is needed (e.g. adb reverse), automatically retry with the other
api.interceptors.response.use(
  (response) => {
    // If the server returned an HTML document (SPA fallback) instead of JSON for an API call, treat as error
    if (typeof response.data === 'string' && response.data.trim().startsWith('<!')) {
      const error = new Error('Received HTML response instead of JSON from API endpoint')
      error.config = response.config
      return Promise.reject(error)
    }
    return response
  },
  async (error) => {
    const config = error.config
    if (!config || config.__retryMobile) {
      return Promise.reject(error)
    }

    if (error.message?.includes('Network Error') || error.code === 'ERR_NETWORK' || error.message?.includes('HTML response')) {
      if (config.baseURL?.includes('10.0.2.2:5000')) {
        config.__retryMobile = true
        config.baseURL = config.baseURL.replace('10.0.2.2:5000', '127.0.0.1:5000')
        return api(config)
      } else if (config.baseURL?.includes('127.0.0.1:5000')) {
        config.__retryMobile = true
        config.baseURL = config.baseURL.replace('127.0.0.1:5000', '10.0.2.2:5000')
        return api(config)
      }
    }
    return Promise.reject(error)
  }
)

export default api
