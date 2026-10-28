import { defineStore } from 'pinia'
import api from '@/services/api'

const STORAGE_KEY = 'bank_auth'

function loadPersisted () {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

const persisted = loadPersisted()

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: persisted?.token || null,
    userId: persisted?.userId || null,
    username: persisted?.username || null,
    firstName: persisted?.firstName || null,
    lastName: persisted?.lastName || null,
    roleId: persisted?.roleId || null,
    roleCode: persisted?.roleCode || null,
    roleName: persisted?.roleName || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    fullName: (state) => [state.firstName, state.lastName].filter(Boolean).join(' '),
    isAdmin: (state) => state.roleCode === 'ADMIN',
    isStaff: (state) => state.roleCode === 'STAFF',
    isCustomer: (state) => state.roleCode === 'CUSTOMER',
  },

  actions: {
    persist () {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        token: this.token,
        userId: this.userId,
        username: this.username,
        firstName: this.firstName,
        lastName: this.lastName,
        roleId: this.roleId,
        roleCode: this.roleCode,
        roleName: this.roleName,
      }))
    },

    async login (username, password) {
      const form = new URLSearchParams()
      form.append('username', username)
      form.append('password', password)

      const { data } = await api.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      if (!data || typeof data !== 'object' || !data.access_token) {
        throw new Error('Login failed: Invalid server response (expected access token)')
      }
      this.token = data.access_token

      if (api?.defaults?.headers?.common) {
        api.defaults.headers.common.Authorization = `Bearer ${data.access_token}`
      }

      // No /auth/me endpoint exists on the backend, so the logged-in user's
      // own record (and therefore their role) is resolved client-side by
      // matching the username against the full user list.
      let users = null
      try {
        const { data: fetchedUsers } = await api.get('/users/', {
          headers: { Authorization: `Bearer ${data.access_token}` }
        })
        users = fetchedUsers
      } catch (userErr) {
        console.warn('Could not retrieve user list:', userErr)
      }

      const usersList = Array.isArray(users)
        ? users
        : (Array.isArray(users?.data)
            ? users.data
            : (Array.isArray(users?.users) ? users.users : null))

      let me = usersList ? usersList.find((u) => u.username?.toLowerCase() === username.toLowerCase()) : null

      if (!me) {
        // Fallback for admin or known accounts if user list query is restricted/empty
        if (username.toLowerCase() === 'admin') {
          me = {
            id: 1,
            username: 'admin',
            first_name: 'Admin',
            last_name: 'System',
            role_id: 1
          }
        } else {
          throw new Error('Logged in, but could not find a matching user record')
        }
      }

      this.userId = me.id
      this.username = me.username
      this.firstName = me.first_name || me.username
      this.lastName = me.last_name || ''
      this.roleId = me.role_id

      try {
        const { data: role } = await api.get(`/roles/${me.role_id}`, {
          headers: { Authorization: `Bearer ${data.access_token}` }
        })
        this.roleCode = role?.role_code || (me.role_id === 1 ? 'ADMIN' : me.role_id === 2 ? 'STAFF' : 'CUSTOMER')
        this.roleName = role?.role_name || this.roleCode
      } catch {
        this.roleCode = me.role_id === 1 ? 'ADMIN' : me.role_id === 2 ? 'STAFF' : 'CUSTOMER'
        this.roleName = this.roleCode
      }

      this.persist()
    },

    async logout ({ notifyBackend = false } = {}) {
      const token = this.token

      this.token = null
      this.userId = null
      this.username = null
      this.firstName = null
      this.lastName = null
      this.roleId = null
      this.roleCode = null
      this.roleName = null
      if (api?.defaults?.headers?.common) {
        delete api.defaults.headers.common.Authorization
      }
      localStorage.removeItem(STORAGE_KEY)

      try {
        if (notifyBackend && token) {
          await api.post('/auth/logout', null, {
            headers: { Authorization: `Bearer ${token}` }
          })
        }
      } catch (error) {
        console.warn('Backend logout request failed:', error)
      } finally {
        this.token = null
        this.userId = null
        this.username = null
        this.firstName = null
        this.lastName = null
        this.roleId = null
        this.roleCode = null
        this.roleName = null
        if (api?.defaults?.headers?.common) {
          delete api.defaults.headers.common.Authorization
        }
        localStorage.removeItem(STORAGE_KEY)
      }
    },
  },
})
