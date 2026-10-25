<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Top Modern App Header ($1M Specification) -->
    <q-header elevated class="million-app-header safe-area-top">
      <q-toolbar class="q-py-xs">
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          class="q-mr-xs"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />

        <q-toolbar-title
          shrink
          class="row items-center no-wrap cursor-pointer q-px-xs"
          style="overflow: visible;"
          @click="router.push('/')"
        >
          <BrandLogo
            :size="36"
            :with-text="true"
            :with-year="true"
            subtitle="Digital Banking System"
            theme="dark"
          />
        </q-toolbar-title>

        <q-space />

        <!-- Role Badge (Desktop) -->
        <q-chip
          v-if="auth.roleName"
          icon="verified_user"
          class="gt-xs text-weight-bold shadow-1 q-mr-sm"
          style="background: rgba(229, 197, 131, 0.12) !important; color: #E5C583 !important; border: 1px solid rgba(229, 197, 131, 0.35);"
        >
          {{ auth.roleName }}
        </q-chip>

        <!-- User Profile Pill -->
        <div class="row items-center gt-sm q-mr-md" style="background: rgba(229, 197, 131, 0.08); border: 1px solid rgba(229, 197, 131, 0.22); padding: 4px 12px; border-radius: 20px;">
          <q-avatar size="26px" class="text-weight-bold" style="font-size: 0.75rem; background: linear-gradient(135deg, #FBF0D9 0%, #E5C583 100%) !important; color: #08090C !important;">
            {{ (auth.fullName || auth.username || 'U').charAt(0).toUpperCase() }}
          </q-avatar>
          <span class="q-ml-sm text-weight-medium text-white text-caption">{{ auth.fullName || auth.username }}</span>
        </div>

        <!-- Live Notifications Button & Flyout -->
        <q-btn flat dense round icon="notifications" aria-label="Notifications" class="q-mr-xs">
          <q-badge
            v-if="unreadCount > 0"
            color="red-6"
            floating
            rounded
            class="shadow-1"
          >
            {{ unreadCount > 99 ? '99+' : unreadCount }}
          </q-badge>

          <q-menu anchor="bottom right" self="top right" :offset="[0, 8]" @show="loadNotifications">
            <q-card style="min-width: 330px; max-width: 94vw" class="shadow-lg">
              <q-card-section class="row items-center justify-between q-py-sm q-px-md bg-lavender-soft-gradient">
                <div class="row items-center">
                  <q-icon name="notifications_active" color="primary" size="20px" class="q-mr-xs" />
                  <span class="text-subtitle2 text-weight-bolder text-white">Notifications</span>
                  <q-badge v-if="unreadCount > 0" color="primary" class="q-ml-xs text-weight-bold">{{ unreadCount }}</q-badge>
                </div>
                <q-btn
                  flat
                  dense
                  size="xs"
                  color="primary"
                  label="Mark all read"
                  :disable="unreadCount === 0"
                  class="text-weight-bold"
                  @click.stop="markAllAsRead"
                />
              </q-card-section>

              <q-separator />

              <q-card-section v-if="notifications.length === 0" class="text-secondary text-center q-pa-lg">
                <q-icon name="done_all" size="36px" color="primary" class="q-mb-xs block" style="margin: 0 auto;" />
                <div class="text-caption text-secondary">You're all caught up!</div>
              </q-card-section>

              <q-list v-else separator style="max-height: 380px; overflow-y: auto">
                <q-item
                  v-for="item in notifications"
                  :key="item.id"
                  clickable
                  :style="!item.is_read ? 'background-color: rgba(229, 197, 131, 0.08);' : ''"
                  @click="markAsRead(item)"
                >
                  <q-item-section avatar top style="min-width: 36px; padding-right: 8px;">
                    <q-avatar size="28px" :style="!item.is_read ? 'background: rgba(229, 197, 131, 0.2); color: #E5C583;' : 'background: rgba(255, 255, 255, 0.08); color: #C5BFB5;'">
                      <q-icon name="mail" size="16px" />
                    </q-avatar>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-weight-bold text-caption text-white">
                      {{ item.title }}
                    </q-item-label>
                    <q-item-label caption style="color: #C5BFB5;">{{ item.message }}</q-item-label>
                    <q-item-label caption style="color: #A39F93; font-size: 0.68rem;" class="q-mt-xs">
                      {{ formatNotificationDate(item.created_at) }}
                    </q-item-label>
                  </q-item-section>
                  <q-item-section v-if="!item.is_read" side>
                    <q-icon name="circle" color="primary" size="8px" />
                  </q-item-section>
                </q-item>
              </q-list>

              <q-separator />
              <q-card-actions align="right" class="q-py-xs q-px-sm" style="background: rgba(229, 197, 131, 0.04);">
                <q-btn flat dense size="sm" color="primary" label="Refresh" icon="refresh" @click="loadNotifications" />
              </q-card-actions>
            </q-card>
          </q-menu>
        </q-btn>

        <!-- Logout Button -->
        <q-btn flat dense round icon="logout" aria-label="Logout" class="q-ml-xs" @click="onLogout">
          <q-tooltip>Sign Out</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <!-- Modern Sidebar Navigation Drawer -->
    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      :width="270"
      class="sidebar-drawer"
    >
      <div class="fit column no-wrap justify-between" style="height: 100%; overflow: hidden;">
        <!-- Drawer Header Identity (Pinned at Top) -->
        <div class="q-pa-md row items-center justify-between border-bottom-subtle" style="flex-shrink: 0; background: rgba(255, 255, 255, 0.02);">
          <div class="column">
            <BrandLogo
              :size="36"
              :with-text="true"
              subtitle="Digital Banking"
              theme="dark"
            />
            <div class="q-mt-sm">
              <div class="text-subtitle1 text-weight-bolder leading-tight" style="color: #FFFFFF;">
                Welcome Back, {{ auth.firstName || (auth.fullName || auth.username || 'User').split(' ')[0] }}
              </div>
              <div class="text-caption text-secondary" style="font-size: 0.72rem;">
                Secure Digital Portal
              </div>
            </div>
          </div>
          <!-- Close button for mobile screens -->
          <q-btn
            flat
            round
            dense
            icon="chevron_left"
            color="primary"
            class="lt-md self-start"
            @click="leftDrawerOpen = false"
          >
            <q-tooltip>Close Menu</q-tooltip>
          </q-btn>
        </div>

        <!-- Scrollable Navigation Items -->
        <div class="col" style="overflow-y: auto; overflow-x: hidden;">
          <q-list class="q-py-sm">
            <q-item-label header>Overview</q-item-label>
            <q-item clickable to="/" exact>
              <q-item-section avatar><q-icon name="dashboard" /></q-item-section>
              <q-item-section>Dashboard</q-item-section>
            </q-item>

            <!-- ADMIN: System Configuration -->
            <template v-if="auth.isAdmin">
              <q-separator spaced class="q-my-sm" />
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

            <!-- ADMIN + STAFF: Banking Operations -->
            <template v-if="auth.isAdmin || auth.isStaff">
              <q-separator spaced class="q-my-sm" />
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

            <!-- CUSTOMER: Self-Service -->
            <template v-if="auth.isCustomer">
              <q-separator spaced class="q-my-sm" />
              <q-item-label header>My Banking</q-item-label>
              <q-item clickable to="/my-account">
                <q-item-section avatar><q-icon name="account_balance_wallet" /></q-item-section>
                <q-item-section>My Account</q-item-section>
              </q-item>
              <q-item clickable to="/my-transactions">
                <q-item-section avatar><q-icon name="receipt_long" /></q-item-section>
                <q-item-section>My Transactions</q-item-section>
              </q-item>
            </template>
          </q-list>
        </div>

        <!-- Drawer Bottom User Profile Widget (Pinned at Bottom) -->
        <div class="q-pa-md border-top-subtle" style="flex-shrink: 0; background: rgba(229, 197, 131, 0.03);">
          <div class="row items-center no-wrap">
            <q-avatar size="36px" class="text-weight-bold shadow-1" style="background: linear-gradient(135deg, #FBF0D9 0%, #E5C583 100%); color: #08090C;">
              {{ (auth.fullName || auth.username || 'U').charAt(0).toUpperCase() }}
            </q-avatar>
            <div class="column q-ml-sm overflow-hidden" style="flex: 1;">
              <span class="text-weight-bold text-caption ellipsis" style="color: #FFFFFF;">{{ auth.fullName || auth.username }}</span>
              <span class="text-caption ellipsis" style="color: #E5C583; font-size: 0.7rem; font-weight: 600;">{{ auth.roleName || 'User' }}</span>
            </div>
            <q-btn flat round dense icon="logout" color="primary" size="sm" @click="onLogout">
              <q-tooltip>Logout</q-tooltip>
            </q-btn>
          </div>
        </div>
      </div>
    </q-drawer>

    <!-- Main Content Container -->
    <q-page-container>
      <router-view />
    </q-page-container>

    <!-- Mobile / Android Native Bottom Navigation Bar (Visible on mobile screens) -->
    <div class="mobile-bottom-nav lt-sm">
      <router-link to="/" class="mobile-nav-item" :class="{ active: $route.path === '/' }">
        <div class="nav-icon-wrap">
          <q-icon name="dashboard" size="20px" />
        </div>
        <span>Home</span>
      </router-link>

      <!-- Customer destinations -->
      <template v-if="auth.isCustomer">
        <router-link to="/my-account" class="mobile-nav-item" :class="{ active: $route.path === '/my-account' }">
          <div class="nav-icon-wrap">
            <q-icon name="account_balance_wallet" size="20px" />
          </div>
          <span>Account</span>
        </router-link>

        <router-link to="/my-transactions" class="mobile-nav-item" :class="{ active: $route.path === '/my-transactions' }">
          <div class="nav-icon-wrap">
            <q-icon name="receipt_long" size="20px" />
          </div>
          <span>Activity</span>
        </router-link>
      </template>

      <!-- Staff destinations -->
      <template v-else-if="auth.isStaff">
        <router-link to="/accounts" class="mobile-nav-item" :class="{ active: $route.path === '/accounts' }">
          <div class="nav-icon-wrap">
            <q-icon name="account_box" size="20px" />
          </div>
          <span>Accounts</span>
        </router-link>

        <router-link to="/deposits" class="mobile-nav-item" :class="{ active: $route.path === '/deposits' }">
          <div class="nav-icon-wrap">
            <q-icon name="add_card" size="20px" />
          </div>
          <span>Deposits</span>
        </router-link>

        <router-link to="/withdrawals" class="mobile-nav-item" :class="{ active: $route.path === '/withdrawals' }">
          <div class="nav-icon-wrap">
            <q-icon name="remove_circle" size="20px" />
          </div>
          <span>Withdraw</span>
        </router-link>
      </template>

      <!-- Admin destinations -->
      <template v-else-if="auth.isAdmin">
        <router-link to="/admin/users" class="mobile-nav-item" :class="{ active: $route.path === '/admin/users' }">
          <div class="nav-icon-wrap">
            <q-icon name="people" size="20px" />
          </div>
          <span>Users</span>
        </router-link>

        <router-link to="/admin/roles" class="mobile-nav-item" :class="{ active: $route.path === '/admin/roles' }">
          <div class="nav-icon-wrap">
            <q-icon name="admin_panel_settings" size="20px" />
          </div>
          <span>Roles</span>
        </router-link>

        <router-link to="/admin/audit-logs" class="mobile-nav-item" :class="{ active: $route.path === '/admin/audit-logs' }">
          <div class="nav-icon-wrap">
            <q-icon name="history" size="20px" />
          </div>
          <span>Audit</span>
        </router-link>
      </template>

      <!-- More / Menu button to trigger Drawer -->
      <button type="button" class="mobile-nav-item" @click="leftDrawerOpen = !leftDrawerOpen">
        <div class="nav-icon-wrap">
          <q-icon name="menu" size="20px" />
        </div>
        <span>Menu</span>
      </button>
    </div>
  </q-layout>
</template>

<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth-store'
import api from '@/services/api'
import BrandLogo from '@/components/BrandLogo.vue'

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
