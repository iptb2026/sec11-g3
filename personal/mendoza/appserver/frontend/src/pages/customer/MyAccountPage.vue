<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Header -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="account_balance_wallet" size="24px" />
        </q-avatar>
        <div>
          <div class="text-h5 text-weight-bolder text-white">My Accounts</div>
          <div class="text-caption text-secondary">View your digital banking cards, available funds, and account limits.</div>
        </div>
      </div>
      <div>
        <q-btn outline color="primary" icon="receipt_long" label="View Transactions" to="/my-transactions" />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center q-pa-xl">
      <q-spinner-dots color="primary" size="48px" />
      <div class="text-caption text-secondary q-mt-sm">Retrieving account records...</div>
    </div>

    <!-- Empty State -->
    <div v-else-if="accounts.length === 0" class="text-center q-pa-xl">
      <q-card class="glass-card q-pa-xl" style="max-width: 480px; margin: 0 auto;">
        <q-icon name="credit_card_off" size="56px" color="primary" class="q-mb-md" />
        <div class="text-h6 text-weight-bold text-white">No Active Accounts Found</div>
        <div class="text-caption text-secondary q-mt-xs">
          No bank account is currently registered under your customer profile. Please contact a bank staff member to open an account for you.
        </div>
      </q-card>
    </div>

    <!-- Accounts Cards Display -->
    <div v-else class="row q-col-gutter-lg">
      <div v-for="acc in accounts" :key="acc.id" class="col-12 col-lg-6">
        <!-- Digital Banking Card Component -->
        <div class="fintech-card q-mb-md">
          <div class="row items-center justify-between no-wrap q-mb-lg">
            <div class="row items-center">
              <BrandLogo :size="24" :with-badge="false" theme="dark" class="q-mr-xs" />
              <span class="text-weight-bold text-subtitle1 tracking-wider text-white">MyBank Digital</span>
            </div>
            <div class="row items-center">
              <q-icon name="contactless" size="26px" class="text-white" style="opacity: 0.85;" />
              <q-badge
                :color="acc.status === 'ACTIVE' ? 'positive' : 'grey-7'"
                class="q-ml-sm text-weight-bolder"
                style="padding: 4px 8px; font-size: 0.7rem; border-radius: 8px;"
              >
                {{ acc.status }}
              </q-badge>
            </div>
          </div>

          <!-- Chip & Card Identifier -->
          <div class="row items-center justify-between q-mb-md">
            <div class="card-chip"></div>
            <div class="text-caption text-weight-medium" style="color: #FCE7EE; opacity: 0.9;">
              {{ acc.currency_code }} Savings Account
            </div>
          </div>

          <!-- Account Number Display with Copy Action -->
          <div class="row items-center justify-between no-wrap q-mb-lg">
            <div class="card-number-display">
              {{ formatAccountNumber(acc.account_number) }}
            </div>
            <q-btn
              flat
              round
              dense
              icon="content_copy"
              color="white"
              size="sm"
              @click.stop="copyAccountNumber(acc.account_number)"
            >
              <q-tooltip>Copy Account Number</q-tooltip>
            </q-btn>
          </div>

          <!-- Balance Showcase -->
          <div class="row items-end justify-between">
            <div>
              <div class="text-caption text-uppercase text-weight-medium" style="color: #FCE7EE; font-size: 0.72rem; letter-spacing: 0.05em;">
                Available Balance
              </div>
              <div class="text-h4 text-weight-bolder text-white q-mt-xs">
                ₱{{ format(acc.available_balance) }}
              </div>
            </div>

            <div class="text-right">
              <div class="text-caption text-uppercase" style="color: #FCE7EE; font-size: 0.68rem;">Card Holder</div>
              <div class="text-subtitle2 text-weight-bold text-white ellipsis" style="max-width: 140px;">
                {{ auth.fullName || auth.username }}
              </div>
            </div>
          </div>
        </div>

        <!-- Android S Card Quick Actions Row -->
        <div class="row items-center q-gutter-sm q-mb-md">
          <q-btn
            unelevated
            color="primary"
            icon="receipt_long"
            label="Transactions"
            to="/my-transactions"
            class="col"
            style="border-radius: 14px;"
          />
          <q-btn
            outline
            color="primary"
            icon="content_copy"
            label="Copy Number"
            class="col"
            style="border-radius: 14px;"
            @click="copyAccountNumber(acc.account_number)"
          />
        </div>

        <!-- Account Metadata Details Card (Material 3 Container) -->
        <q-card class="shadow-sm border-subtle q-mb-lg" style="border-radius: 20px;">
          <q-card-section class="q-pa-md">
            <div class="row q-col-gutter-md">
              <div class="col-6 col-sm-3">
                <div class="text-caption text-weight-medium text-secondary">Ledger Balance</div>
                <div class="text-subtitle1 text-weight-bold text-white">₱{{ format(acc.ledger_balance) }}</div>
              </div>
              <div class="col-6 col-sm-3">
                <div class="text-caption text-weight-medium text-secondary">Currency</div>
                <div class="text-subtitle1 text-weight-bold text-white">{{ acc.currency_code }}</div>
              </div>
              <div class="col-6 col-sm-3">
                <div class="text-caption text-weight-medium text-secondary">Branch</div>
                <div class="text-subtitle1 text-weight-bold text-white">{{ acc.branch_code || 'Central' }}</div>
              </div>
              <div class="col-6 col-sm-3">
                <div class="text-caption text-weight-medium text-secondary">Date Opened</div>
                <div class="text-subtitle1 text-weight-bold text-white">{{ acc.opened_at?.slice(0, 10) || '—' }}</div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Notify } from 'quasar'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'
import BrandLogo from '@/components/BrandLogo.vue'

const auth = useAuthStore()
const accounts = ref([])
const loading = ref(true)

function format (val) {
  return Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatAccountNumber (val) {
  if (!val) return '•••• •••• ••••'
  const str = String(val).replace(/\s+/g, '')
  return str.match(/.{1,4}/g)?.join(' ') || str
}

async function copyAccountNumber (val) {
  if (!val) return
  try {
    await navigator.clipboard.writeText(String(val))
    Notify.create({
      type: 'positive',
      message: `Account number ${val} copied to clipboard!`,
      position: 'top',
      timeout: 2000,
    })
  } catch {
    Notify.create({
      type: 'info',
      message: `Account: ${val}`,
      position: 'top',
    })
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/accounts/')
    accounts.value = data.filter((a) => a.customer_id === auth.userId)
  } finally {
    loading.value = false
  }
})
</script>
