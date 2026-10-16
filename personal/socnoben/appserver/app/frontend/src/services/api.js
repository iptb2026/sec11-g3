import axios from 'axios'

const api = axios.create({
  baseURL: ''
})

api.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem('bank_auth')
    if (raw) {
      const parsed = JSON.parse(raw)
      if (parsed && parsed.token) {
        config.headers.Authorization = `Bearer ${parsed.token}`
      }
    }
  } catch (e) {}
  return config
})

export default api
