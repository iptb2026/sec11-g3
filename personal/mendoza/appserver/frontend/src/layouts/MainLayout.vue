<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />

        <q-toolbar-title>
          <q-icon name="account_balance" class="q-mr-sm" />
          Mini Banking System
        </q-toolbar-title>

        <q-chip
          v-if="auth.roleName"
          square
          color="white"
          text-color="primary"
          icon="badge"
          class="q-mr-md"
        >
          {{ auth.roleName }}
        </q-chip>

        <div class="q-mr-md">{{ auth.fullName || auth.username }}</div>

        <q-btn flat dense round icon="notifications" aria-label="Notifications">
          <q-badge
            v-if="unreadCount > 0"
            color="red"
            floating
            rounded
          >
            {{ unreadCount > 99 ? '99+' : unreadCount }}
          </q-badge>

          <q-menu anchor="bottom right" self="top right" @show="loadNotifications">
            <q-card style="min-width: 320px; max-width: 92vw">
              <q-card-section class="row items-center justify-between q-pb-sm">
                <div class="text-subtitle1 text-weight-bold">Notifications</div>
                <q-btn
                  flat
                  dense
                  size="sm"
                  label="Mark all read"
                  :disable="unreadCount === 0"
                  @click.stop="markAllAsRead"
                />
              </q-card-section>

              <q-separator />

              <q-card-section v-if="notifications.length === 0" class="text-grey text-center q-pa-lg">
                You're all caught up.
              </q-card-section>

              <q-list v-else separator style="max-height: 360px; overflow-y: auto">
                <q-item
                  v-for="item in notifications"
                  :key="item.id"
                  clickable
                  :class="{ 'bg-blue-1': !item.is_read }"
                  @click="markAsRead(item)"
                >
                  <q-item-section>
                    <q-item-label class="text-weight-medium">
                      {{ item.title }}
                    </q-item-label>
                    <q-item-label caption>{{ item.message }}</q-item-label>
                    <q-item-label caption>{{ formatNotificationDate(item.created_at) }}</q-item-label>
                  </q-item-section>
                  <q-item-section v-if="!item.is_read" side>
                    <q-icon name="circle" color="primary" size="9px" />
                  </q-item-section>
                </q-item>
              </q-list>

              <q-separator />
              <q-card-actions align="right">
                <q-btn flat dense label="Refresh" icon="refresh" @click="loadNotifications" />
              </q-card-actions>
            </q-card>
          </q-menu>
        </q-btn>

        <q-btn flat dense round icon="logout" aria-label="Logout" @click="onLogout" />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-list>
        <q-item-label header>Navigation</q-item-label>

        <q-item clickable to="/" exact>
          <q-item-section avatar><q-icon name="dashboard" /></q-item-section>
          <q-item-section>Dashboard</q-item-section>
        </q-item>

        <template v-if="auth.isAdmin">
          <q-separator spaced />
          <q-item-label header>System Configuration</q-item-label>
          <q-item clickable to="/admin/roles">
            <q-item-section avatar><q-icon name="admin_panel_settings" /></q-item-section>
            <q-item-section>Roles</q-item-section>
          </q-item>
          <q-item clickable to="/admin/account-types">
            <q-item-section avatar><q-icon name="category" /></q-item-section>
            <q-item-section>Account Types</q-item-section>
          </q-item>
          <q-item clickable to="/admin/banks">
            <q-item-section avatar><q-icon name="account_balance" /></q-item-section>
            <q-item-section>Banks</q-item-section>
          </q-item>
          <q-item clickable to="/admin/fee-types">
            <q-item-section avatar><q-icon name="sell" /></q-item-section>
            <q-item-section>Fee Types</q-item-section>
          </q-item>
          <q-item clickable to="/admin/users">
            <q-item-section avatar><q-icon name="people" /></q-item-section>
            <q-item-section>Users</q-item-section>
          </q-item>
          <q-item clickable to="/admin/audit-logs">
            <q-item-section avatar><q-icon name="history" /></q-item-section>
            <q-item-section>Audit Logs</q-item-section>
          </q-item>
        </template>

        <template v-if="auth.isAdmin || auth.isStaff">
          <q-separator spaced />
          <q-item-label header>Banking Operations</q-item-label>
          <q-item clickable to="/accounts">
            <q-item-section avatar><q-icon name="account_box" /></q-item-section>
            <q-item-section>Accounts</q-item-section>
          </q-item>
          <q-item clickable to="/withdrawal-limits">
            <q-item-section avatar><q-icon name="speed" /></q-item-section>
            <q-item-section>Withdrawal Limits</q-item-section>
          </q-item>
          <q-item clickable to="/interest-policies">
            <q-item-section avatar><q-icon name="percent" /></q-item-section>
            <q-item-section>Interest Policies</q-item-section>
          </q-item>
          <q-item clickable to="/deposits">
            <q-item-section avatar><q-icon name="add_card" /></q-item-section>
            <q-item-section>Deposits</q-item-section>
          </q-item>
          <q-item clickable to="/withdrawals">
            <q-item-section avatar><q-icon name="remove_circle" /></q-item-section>
            <q-item-section>Withdrawals</q-item-section>
          </q-item>
          <q-item clickable to="/transfers">
            <q-item-section avatar><q-icon name="swap_horiz" /></q-item-section>
            <q-item-section>Transfers</q-item-section>
          </q-item>
          <q-item clickable to="/interbank-transfers">
            <q-item-section avatar><q-icon name="sync_alt" /></q-item-section>
            <q-item-section>Interbank Transfers</q-item-section>
          </q-item>
          <q-item clickable to="/fee-records">
            <q-item-section avatar><q-icon name="receipt_long" /></q-item-section>
            <q-item-section>Fee Records</q-item-section>
          </q-item>
          <q-item clickable to="/interest-records">
            <q-item-section avatar><q-icon name="savings" /></q-item-section>
            <q-item-section>Interest Records</q-item-section>
          </q-item>
          <q-item clickable to="/ledger-entries">
            <q-item-section avatar><q-icon name="menu_book" /></q-item-section>
            <q-item-section>Ledger Entries</q-item-section>
          </q-item>
        </template>

        <template v-if="auth.isCustomer">
          <q-separator spaced />
          <q-item-label header>My Banking</q-item-label>
          <q-item clickable to="/my-account">
            <q-item-section avatar><q-icon name="account_box" /></q-item-section>
            <q-item-section>My Account</q-item-section>
          </q-item>
          <q-item clickable to="/my-transactions">
            <q-item-section avatar><q-icon name="receipt_long" /></q-item-section>
            <q-item-section>My Transactions</q-item-section>
          </q-item>
        </template>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth-store'
import api from '@/services/api'

const leftDrawerOpen = ref(false)
const auth = useAuthStore()
const router = useRouter()

const notifications = ref([])
const unreadCount = ref(0)
let notificationSocket = null

function authConfig () {
  return {
    headers: {
      Authorization: `Bearer ${auth.token}`,
    },
  }
}

async function loadNotifications () {
  if (!auth.token) return

  try {
    const { data } = await api.get('/notifications/', authConfig())
    notifications.value = data.notifications || []
    unreadCount.value = data.unread_count || 0
  } catch (error) {
    console.error('Could not load notifications:', error)
  }
}

async function markAsRead (item) {
  if (item.is_read || !auth.token) return

  try {
    await api.patch(`/notifications/${item.id}/read`, {}, authConfig())
    item.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch (error) {
    console.error('Could not mark notification as read:', error)
  }
}

async function markAllAsRead () {
  if (!auth.token || unreadCount.value === 0) return

  try {
    await api.patch('/notifications/read-all', {}, authConfig())
    notifications.value.forEach((item) => {
      item.is_read = true
    })
    unreadCount.value = 0
  } catch (error) {
    console.error('Could not mark all notifications as read:', error)
  }
}

function formatNotificationDate (value) {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleString()
}

function connectNotifications () {
  if (!auth.token) return

  try {
    const url = new URL(api.defaults.baseURL || window.location.origin, window.location.href)
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
    url.pathname = `${url.pathname.replace(/\/$/, '')}/notifications/ws`
    url.search = ''
    url.searchParams.set('token', auth.token)

    notificationSocket = new WebSocket(url.toString())

    notificationSocket.onmessage = (event) => {
      try {
        const item = JSON.parse(event.data)
        const alreadyExists = notifications.value.some(
          (notification) => notification.id === item.id,
        )

        if (!alreadyExists) {
          notifications.value.unshift(item)
          notifications.value = notifications.value.slice(0, 100)
          if (!item.is_read) unreadCount.value += 1
        }
      } catch (error) {
        console.error('Invalid notification message:', error)
      }
    }

    notificationSocket.onerror = () => {
      console.warn('Notification live connection encountered an error.')
    }
  } catch (error) {
    console.error('Could not connect to live notifications:', error)
  }
}

function closeNotifications () {
  if (notificationSocket) {
    notificationSocket.close()
    notificationSocket = null
  }
}

async function onLogout () {
  closeNotifications()
  await auth.logout({ notifyBackend: true })
  notifications.value = []
  unreadCount.value = 0
  router.push('/login')
}

watch(
  () => auth.token,
  (token) => {
    closeNotifications()
    notifications.value = []
    unreadCount.value = 0

    if (token) {
      loadNotifications()
      connectNotifications()
    }
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  closeNotifications()
})
</script>
