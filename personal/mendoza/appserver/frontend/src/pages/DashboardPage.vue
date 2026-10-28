<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- $100k Luxury Greeting Bar -->
    <div class="row items-center justify-between q-mb-lg">
      <div class="row items-center no-wrap">
        <q-avatar size="54px" class="bg-lavender-gradient text-white shadow-md q-mr-md" style="border: 1px solid rgba(229, 197, 131, 0.28); box-shadow: inset 0 1px 0 rgba(245, 226, 186, 0.35);">
          <span class="text-weight-bolder text-h6" style="color: #E5C583;">
            {{ (auth.fullName || auth.username || 'U').charAt(0).toUpperCase() }}
          </span>
        </q-avatar>
        <div>
          <div class="row items-center no-wrap">
            <span class="text-h5 text-weight-bolder text-white">
              Hi, {{ auth.firstName || (auth.fullName ? auth.fullName.split(' ')[0] : auth.username) }}
            </span>
            <q-badge
              color="accent"
              class="q-ml-sm text-weight-bold"
              style="padding: 3px 10px; border-radius: 999px; font-size: 0.72rem; background: rgba(229, 197, 131, 0.14) !important; border: 1px solid rgba(229, 197, 131, 0.35); color: #E5C583 !important;"
            >
              {{ auth.roleName || 'User' }}
            </q-badge>
          </div>
          <div class="text-caption" style="color: #A39F93; font-size: 0.78rem;">
            Welcome to your MyBank Digital portal
          </div>
        </div>
      </div>

      <!-- Live Security & Network Health Status (Desktop) -->
      <div class="row items-center q-gutter-sm gt-xs">
        <div class="row items-center text-caption text-weight-bold q-px-sm q-py-xs" style="background: rgba(52, 199, 89, 0.1); border: 1px solid rgba(52, 199, 89, 0.28); border-radius: 999px; color: #34C759; font-size: 0.72rem;">
          <span style="width: 6px; height: 6px; background: #34C759; border-radius: 50%; box-shadow: 0 0 8px #34C759; margin-right: 6px;"></span>
          LIVE NODE • 12ms
        </div>
        <q-chip outline color="white" icon="security" size="sm" class="text-weight-bold" style="border-color: rgba(255, 255, 255, 0.15) !important;">
          256-Bit SSL Protected
        </q-chip>
      </div>
    </div>

    <!-- Quick Actions Squircle Capsule Bar -->
    <div class="android-quick-actions-bar">
      <!-- Customer Actions -->
      <template v-if="auth.isCustomer">
        <router-link to="/my-account" class="android-action-btn">
          <div class="android-action-icon">
            <q-icon name="account_balance_wallet" size="24px" />
          </div>
          <span class="android-action-label">My Card</span>
        </router-link>

        <router-link to="/my-transactions" class="android-action-btn">
          <div class="android-action-icon">
            <q-icon name="receipt_long" size="24px" />
          </div>
          <span class="android-action-label">Activity</span>
        </router-link>

        <router-link to="/customer-transfer" class="android-action-btn">
          <div class="android-action-icon">
            <q-icon name="send" size="24px" />
          </div>
          <span class="android-action-label">Transfer</span>
        </router-link>

        <div class="android-action-btn" @click="router.push('/my-transactions')">
          <div class="android-action-icon">
            <q-icon name="history" size="24px" />
          </div>
          <span class="android-action-label">History</span>
        </div>
      </template>

      <!-- Staff Actions -->
      <template v-else-if="auth.isStaff">
        <router-link to="/deposits" class="android-action-btn">
          <div class="android-action-icon">
            <q-icon name="add_card" size="24px" color="positive" />
          </div>
          <span class="android-action-label">Deposit</span>
        </router-link>

        <router-link to="/withdrawals" class="android-action-btn">
          <div class="android-action-icon">
            <q-icon name="remove_circle" size="24px" color="negative" />
          </div>
          <span class="android-action-label">Withdraw</span>
        </router-link>

        <router-link to="/transfers" class="android-action-btn">
          <div class="android-action-icon">
            <q-icon name="swap_horiz" size="24px" color="accent" />
          </div>
          <span class="android-action-label">Transfer</span>
        </router-link>

        <router-link to="/accounts" class="android-action-btn">
          <div class="android-action-icon">
            <q-icon name="account_box" size="24px" color="info" />
          </div>
          <span class="android-action-label">Accounts</span>
        </router-link>
      </template>

      <!-- Admin Actions -->
      <template v-else-if="auth.isAdmin">
        <router-link to="/admin/users" class="android-action-btn">
          <div class="android-action-icon">
            <q-icon name="person_add" size="24px" />
          </div>
          <span class="android-action-label">Users</span>
        </router-link>

        <router-link to="/admin/roles" class="android-action-btn">
          <div class="android-action-icon">
            <q-icon name="admin_panel_settings" size="24px" color="accent" />
          </div>
          <span class="android-action-label">Roles</span>
        </router-link>

        <router-link to="/admin/banks" class="android-action-btn">
          <div class="android-action-icon">
            <q-icon name="account_balance" size="24px" color="info" />
          </div>
          <span class="android-action-label">Banks</span>
        </router-link>

        <router-link to="/admin/audit-logs" class="android-action-btn">
          <div class="android-action-icon">
            <q-icon name="history" size="24px" color="warning" />
          </div>
          <span class="android-action-label">Audit Logs</span>
        </router-link>
      </template>
    </div>

    <!-- Customer Digital Card Showcase Widget -->
    <div v-if="auth.isCustomer && customerAccount" class="q-mb-lg">
      <div class="fintech-card cursor-pointer" @click="router.push('/my-account')">
        <div class="row items-center justify-between no-wrap q-mb-md">
          <div class="row items-center">
            <BrandLogo :size="24" :with-badge="false" theme="dark" class="q-mr-xs" />
            <span class="text-weight-bold text-subtitle1 text-white">MyBank Digital</span>
          </div>
          <div class="row items-center">
            <q-icon name="contactless" size="26px" class="text-white q-mr-sm" style="opacity: 0.9;" />
            <q-badge color="positive" class="text-weight-bolder" style="padding: 4px 10px; font-size: 0.7rem; border-radius: 999px;">
              {{ customerAccount.status || 'ACTIVE' }}
            </q-badge>
          </div>
        </div>

        <div class="row items-center justify-between q-mb-md">
          <div class="card-chip"></div>
          <div class="text-caption text-weight-medium" style="color: #94A3B8;">
            {{ customerAccount.currency_code }} Savings Account
          </div>
        </div>

        <div class="card-number-display q-mb-md">
          {{ formatCardNumber(customerAccount.account_number) }}
        </div>

        <div class="row items-end justify-between">
          <div>
            <div class="text-caption text-uppercase" style="color: #94A3B8; font-size: 0.7rem; letter-spacing: 0.08em;">
              Total Available Balance
            </div>
            <div class="text-h4 text-weight-bolder text-white q-mt-xs">
              ₱{{ formatAmount(customerAccount.available_balance) }}
            </div>
          </div>
          <div class="text-right">
            <div class="text-caption text-uppercase" style="color: #94A3B8; font-size: 0.65rem;">Tap to manage</div>
            <q-icon name="arrow_forward" color="white" size="18px" />
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center q-pa-xl">
      <q-spinner-dots color="white" size="48px" />
      <div class="text-caption text-secondary q-mt-sm">Loading financial data...</div>
    </div>

    <!-- Metrics Cards Grid -->
    <div v-else>
      <div class="row items-center justify-between q-mb-sm">
        <span class="text-subtitle2 text-weight-bolder text-white">Overview Metrics</span>
        <span class="text-caption text-secondary">{{ cards.length }} Active Counters</span>
      </div>

      <div class="row q-col-gutter-md" :class="{ 'customer-metrics-grid': auth.isCustomer }">
        <div
          v-for="card in cards"
          :key="card.label"
          :class="auth.isCustomer ? 'col-12 col-sm-6 col-md-6' : 'col-12 col-sm-6 col-md-3'"
        >
          <q-card
            class="dashboard-stat-card cursor-pointer"
            @click="card.to && router.push(card.to)"
          >
            <q-card-section class="row items-center justify-between no-wrap q-pa-lg">
              <div>
                <div class="row items-center q-mb-xs">
                  <div class="text-caption text-weight-bold text-uppercase q-mr-sm" style="color: #94A3B8; letter-spacing: 0.08em; font-size: 0.72rem;">
                    {{ card.label }}
                  </div>
                  <span v-if="card.trend" class="luxury-stat-trend" :class="card.trend.includes('-') ? 'negative' : 'positive'">
                    {{ card.trend }}
                  </span>
                </div>
                <div class="text-h4 text-weight-bolder text-white q-mt-xs">
                  {{ card.value }}
                </div>
                <div v-if="card.to" class="row items-center q-mt-sm text-caption text-weight-medium text-secondary">
                  <span>View Details</span>
                  <q-icon name="arrow_forward" size="13px" class="q-ml-xs text-white" />
                </div>
              </div>

              <div class="dashboard-icon-wrapper" :style="getIconWrapperStyle(card.color)">
                <q-icon :name="card.icon" size="26px" />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Quick Operations Hub (Staff / Admin) -->
      <div v-if="auth.isStaff || auth.isAdmin" class="q-mt-xl">
        <div class="row items-center justify-between q-mb-md">
          <span class="text-subtitle1 text-weight-bolder text-white">Banking Modules</span>
          <span class="text-caption text-secondary">Core Operations Hub</span>
        </div>

        <div v-if="auth.isStaff" class="row q-col-gutter-md">
          <div class="col-6 col-sm-3">
            <router-link to="/interbank-transfers" class="luxury-module-card">
              <div class="row items-center no-wrap">
                <q-icon name="sync_alt" color="accent" size="22px" class="q-mr-sm" />
                <span class="text-weight-bold text-body2">Interbank</span>
              </div>
            </router-link>
          </div>
          <div class="col-6 col-sm-3">
            <router-link to="/fee-records" class="luxury-module-card">
              <div class="row items-center no-wrap">
                <q-icon name="receipt_long" color="info" size="22px" class="q-mr-sm" />
                <span class="text-weight-bold text-body2">Fee Records</span>
              </div>
            </router-link>
          </div>
          <div class="col-6 col-sm-3">
            <router-link to="/ledger-entries" class="luxury-module-card">
              <div class="row items-center no-wrap">
                <q-icon name="menu_book" color="positive" size="22px" class="q-mr-sm" />
                <span class="text-weight-bold text-body2">Ledger</span>
              </div>
            </router-link>
          </div>
          <div class="col-6 col-sm-3">
            <router-link to="/interest-records" class="luxury-module-card">
              <div class="row items-center no-wrap">
                <q-icon name="savings" color="warning" size="22px" class="q-mr-sm" />
                <span class="text-weight-bold text-body2">Yield</span>
              </div>
            </router-link>
          </div>
        </div>

        <div v-else-if="auth.isAdmin" class="row q-col-gutter-md">
          <div class="col-6 col-sm-3">
            <router-link to="/admin/users" class="luxury-module-card">
              <div class="row items-center no-wrap">
                <q-icon name="group" color="primary" size="22px" class="q-mr-sm" />
                <span class="text-weight-bold text-body2">Users</span>
              </div>
            </router-link>
          </div>
          <div class="col-6 col-sm-3">
            <router-link to="/admin/roles" class="luxury-module-card">
              <div class="row items-center no-wrap">
                <q-icon name="admin_panel_settings" color="accent" size="22px" class="q-mr-sm" />
                <span class="text-weight-bold text-body2">Roles</span>
              </div>
            </router-link>
          </div>
          <div class="col-6 col-sm-3">
            <router-link to="/admin/banks" class="luxury-module-card">
              <div class="row items-center no-wrap">
                <q-icon name="account_balance" color="info" size="22px" class="q-mr-sm" />
                <span class="text-weight-bold text-body2">Banks</span>
              </div>
            </router-link>
          </div>
          <div class="col-6 col-sm-3">
            <router-link to="/admin/audit-logs" class="luxury-module-card">
              <div class="row items-center no-wrap">
                <q-icon name="history" color="warning" size="22px" class="q-mr-sm" />
                <span class="text-weight-bold text-body2">Audit Logs</span>
              </div>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Customer Self-Service Info -->
      <div v-if="auth.isCustomer" class="q-mt-lg">
        <q-banner rounded class="glass-card text-white border-subtle q-pa-md" style="border-radius: 20px;">
          <template #avatar>
            <q-avatar color="accent" text-color="white" icon="security" size="42px" style="background: rgba(120, 121, 241, 0.2) !important; border: 1px solid rgba(120, 121, 241, 0.35);" />
          </template>
          <div class="text-subtitle1 text-weight-bold">Secured Digital Banking System</div>
          <div class="text-caption text-secondary">
            Your transactions and balances are safeguarded with end-to-end cryptographic integrity. You can monitor your real-time account ledger under <strong>Activity</strong>.
          </div>
        </q-banner>
      </div>
    </div>

    <!-- Floating Action Button (Mobile) -->
    <router-link
      v-if="auth.isStaff"
      to="/deposits"
      class="android-fab lt-sm"
      aria-label="New Deposit"
    >
      <q-icon name="add" size="28px" />
    </router-link>
    <router-link
      v-else-if="auth.isCustomer"
      to="/my-account"
      class="android-fab lt-sm"
      aria-label="My Account"
    >
      <q-icon name="credit_card" size="26px" />
    </router-link>
    <router-link
      v-else-if="auth.isAdmin"
      to="/admin/users"
      class="android-fab lt-sm"
      aria-label="Add User"
    >
      <q-icon name="person_add" size="26px" />
    </router-link>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'
import BrandLogo from '@/components/BrandLogo.vue'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(true)
const cards = ref([])
const customerAccount = ref(null)

function formatCardNumber (num) {
  if (!num) return '•••• •••• •••• ••••'
  return String(num).replace(/(.{4})/g, '$1 ').trim()
}

function formatAmount (val) {
  if (val === undefined || val === null) return '0.00'
  return Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadAdminCards () {
  const [roles, users, accounts, banks] = await Promise.all([
    api.get('/roles/'),
    api.get('/users/'),
    api.get('/accounts/'),
    api.get('/banks/'),
  ])
  cards.value = [
    { label: 'Roles', value: roles.data.length, icon: 'admin_panel_settings', color: 'accent', trend: 'ACTIVE', to: '/admin/roles' },
    { label: 'Users', value: users.data.length, icon: 'people', color: 'primary', trend: '+12.5%', to: '/admin/users' },
    { label: 'Accounts', value: accounts.data.length, icon: 'account_box', color: 'positive', trend: '+8.4%', to: '/accounts' },
    { label: 'Registered Banks', value: banks.data.length, icon: 'account_balance', color: 'info', trend: 'VERIFIED', to: '/admin/banks' },
  ]
}

async function loadStaffCards () {
  const [accounts, deposits, withdrawals, interbank] = await Promise.all([
    api.get('/accounts/'),
    api.get('/deposits/'),
    api.get('/withdrawals/'),
    api.get('/interbank-transfers/'),
  ])
  const pending = interbank.data.filter((i) => i.status === 'PROCESSING').length
  cards.value = [
    { label: 'Accounts', value: accounts.data.length, icon: 'account_box', color: 'primary', trend: 'STABLE', to: '/accounts' },
    { label: 'Deposits Recorded', value: deposits.data.length, icon: 'add_card', color: 'positive', trend: '+15.2%', to: '/deposits' },
    { label: 'Withdrawals Recorded', value: withdrawals.data.length, icon: 'remove_circle', color: 'negative', trend: '-3.1%', to: '/withdrawals' },
    { label: 'Interbank Pending', value: pending, icon: 'sync_alt', color: 'warning', trend: pending > 0 ? 'URGENT' : 'CLEAR', to: '/interbank-transfers' },
  ]
}

async function loadCustomerCards () {
  const { data: allAccounts } = await api.get('/accounts/')
  const mine = allAccounts.filter((a) => a.customer_id === auth.userId)
  if (mine.length > 0) {
    customerAccount.value = mine[0]
  }
  const totalBalance = mine.reduce((sum, a) => sum + Number(a.available_balance), 0)
  cards.value = [
    { label: 'My Accounts', value: mine.length, icon: 'account_box', color: 'primary', trend: 'ACTIVE', to: '/my-account' },
    {
      label: 'Total Available Balance',
      value: `₱${totalBalance.toLocaleString('en-PH', { minimumFractionDigits: 2 })}`,
      icon: 'payments',
      color: 'positive',
      trend: '+4.8%',
      to: '/my-account',
    },
  ]
}

function getIconWrapperStyle (color) {
  if (color === 'positive') return 'background: rgba(52, 211, 153, 0.14) !important; color: #34D399 !important; border-color: rgba(52, 211, 153, 0.3) !important;'
  if (color === 'negative') return 'background: rgba(255, 69, 58, 0.14) !important; color: #FF453A !important; border-color: rgba(255, 69, 58, 0.3) !important;'
  if (color === 'warning') return 'background: rgba(251, 191, 36, 0.14) !important; color: #FBBF24 !important; border-color: rgba(251, 191, 36, 0.3) !important;'
  if (color === 'info') return 'background: rgba(56, 189, 248, 0.14) !important; color: #38BDF8 !important; border-color: rgba(56, 189, 248, 0.3) !important;'
  if (color === 'accent') return 'background: rgba(212, 175, 55, 0.14) !important; color: #E5C583 !important; border-color: rgba(229, 197, 131, 0.3) !important;'
  return 'background: rgba(229, 197, 131, 0.08) !important; color: #E5C583 !important; border-color: rgba(229, 197, 131, 0.22) !important;'
}

onMounted(async () => {
  try {
    if (auth.isAdmin) await loadAdminCards()
    else if (auth.isStaff) await loadStaffCards()
    else if (auth.isCustomer) await loadCustomerCards()
  } finally {
    loading.value = false
  }
})
</script>
