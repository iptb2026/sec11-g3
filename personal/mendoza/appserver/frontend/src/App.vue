<template>
  <router-view />
</template>

<script setup>
import { onBeforeUnmount, onMounted, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth-store'

const IDLE_TIMEOUT_MS = 10 * 60 * 1000
const ACTIVITY_STORAGE_KEY = 'bank_last_activity'

const auth = useAuthStore()
const router = useRouter()
const $q = useQuasar()

let timeoutId
let lastActivityWrite = 0
let loggingOut = false

function storedLastActivity () {
  const value = Number(localStorage.getItem(ACTIVITY_STORAGE_KEY))
  return Number.isFinite(value) && value > 0 ? value : null
}

function scheduleIdleTimeout () {
  clearTimeout(timeoutId)
  if (!auth.isAuthenticated) return

  const lastActivity = storedLastActivity()
  if (lastActivity === null) {
    recordActivity()
    return
  }

  const remaining = IDLE_TIMEOUT_MS - (Date.now() - lastActivity)
  if (remaining <= 0) {
    void logoutForInactivity()
    return
  }

  timeoutId = setTimeout(scheduleIdleTimeout, remaining)
}

function recordActivity () {
  if (!auth.isAuthenticated) return

  const now = Date.now()
  if (now - lastActivityWrite >= 1000) {
    localStorage.setItem(ACTIVITY_STORAGE_KEY, String(now))
    lastActivityWrite = now
  }
  scheduleIdleTimeout()
}

async function logoutForInactivity () {
  if (!auth.isAuthenticated || loggingOut) return
  loggingOut = true
  clearTimeout(timeoutId)
  void auth.logout({ notifyBackend: true })
  await router.replace('/login')
  $q.notify({
    type: 'warning',
    message: 'You were signed out after 10 minutes of inactivity.',
  })
  loggingOut = false
}

function onStorageChange (event) {
  if (event.key === ACTIVITY_STORAGE_KEY) {
    scheduleIdleTimeout()
  } else if (event.key === 'bank_auth' && event.newValue === null && auth.isAuthenticated) {
    void auth.logout().then(() => router.replace('/login'))
  }
}

function onVisibilityChange () {
  if (document.visibilityState === 'visible') scheduleIdleTimeout()
}

watch(
  () => auth.isAuthenticated,
  (isAuthenticated) => {
    clearTimeout(timeoutId)
    if (isAuthenticated) {
      scheduleIdleTimeout()
    } else {
      localStorage.removeItem(ACTIVITY_STORAGE_KEY)
    }
  },
  { immediate: true },
)

onMounted(() => {
  for (const eventName of ['pointerdown', 'keydown', 'touchstart', 'scroll', 'wheel', 'mousemove']) {
    window.addEventListener(eventName, recordActivity, { passive: true })
  }
  window.addEventListener('storage', onStorageChange)
  document.addEventListener('visibilitychange', onVisibilityChange)
})

onBeforeUnmount(() => {
  clearTimeout(timeoutId)
  for (const eventName of ['pointerdown', 'keydown', 'touchstart', 'scroll', 'wheel', 'mousemove']) {
    window.removeEventListener(eventName, recordActivity)
  }
  window.removeEventListener('storage', onStorageChange)
  document.removeEventListener('visibilitychange', onVisibilityChange)
})
</script>
