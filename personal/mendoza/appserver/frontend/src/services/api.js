import axios from 'axios'

function getBaseUrl () {
  const envUrl = import.meta.env.QCLI_API_BASE_URL
  if (envUrl && envUrl.startsWith('http')) {
    return envUrl
  }
  // When running inside Capacitor Android (where origin is https://localhost)
  if (typeof window !== 'undefined' && (window.Capacitor?.isNativePlatform?.() || (window.location.origin === 'https://localhost' && !window.location.port))) {
    return 'http://10.0.2.2:5000/mendoza'
  }
  return envUrl || '/mendoza'
}

const api = axios.create({
  baseURL: getBaseUrl(),
})

// If 10.0.2.2 fails or 127.0.0.1 is needed (e.g. adb reverse), automatically retry with the other
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config
    if (!config || config.__retryMobile) {
      return Promise.reject(error)
    }

    if (error.message?.includes('Network Error') || error.code === 'ERR_NETWORK') {
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
