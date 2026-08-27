import axios from 'axios'

let baseURL = import.meta.env.QCLI_API_BASE_URL || '/carbonilla/'

if (typeof window !== 'undefined' && baseURL.startsWith('http')) {
  try {
    const url = new URL(baseURL)
    if (window.location.hostname !== url.hostname && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
      baseURL = `${window.location.protocol}//${window.location.host}/carbonilla/`
    }
  } catch (e) {
    // ignore
  }
}

const api = axios.create({
  baseURL,
})

export default api
