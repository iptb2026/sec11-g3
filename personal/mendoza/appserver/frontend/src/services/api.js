import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.QCLI_API_BASE_URL || '/mendoza',
})

export default api
