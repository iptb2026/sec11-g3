<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="receipt_long" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder text-white">Transaction Activity</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ filteredRows.length }} Entries
            </q-badge>
          </div>
          <div class="text-caption text-secondary">Complete real-time ledger of your deposits, withdrawals, and transfers.</div>
        </div>
      </div>
      <div>
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Search transactions..."
          class="android-search-pill"
          style="min-width: 220px;"
        >
          <template #prepend>
            <q-icon name="search" color="primary" />
          </template>
          <template v-if="filter" #append>
            <q-icon name="close" class="cursor-pointer" @click="filter = ''" />
          </template>
        </q-input>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center q-pa-xl">
      <q-spinner-dots color="primary" size="48px" />
      <div class="text-caption text-secondary q-mt-sm">Loading your transaction records...</div>
    </div>

    <!-- Empty State -->
    <div v-else-if="rows.length === 0" class="text-center q-pa-xl">
      <q-card class="glass-card q-pa-xl" style="max-width: 440px; margin: 0 auto;">
        <q-icon name="history_toggle_off" size="56px" color="primary" class="q-mb-md" />
        <div class="text-h6 text-weight-bold text-white">No Transactions Yet</div>
        <div class="text-caption text-secondary q-mt-xs">
          You don't have any recorded transactions on your accounts yet.
        </div>
      </q-card>
    </div>

    <!-- Mobile Transaction List Cards (Visible on screens < 600px) -->
    <div v-else class="lt-sm">
      <div v-for="item in filteredRows" :key="item.key" class="transaction-item shadow-sm">
        <div
          class="transaction-icon-box"
          :class="item.direction === 'credit' ? 'credit' : (item.type.includes('TRANSFER') || item.type === 'INTERBANK' ? 'transfer' : 'debit')"
        >
          <q-icon
            :name="item.type === 'DEPOSIT' || item.type === 'TRANSFER IN' ? 'arrow_downward' : (item.type === 'WITHDRAWAL' ? 'arrow_upward' : 'swap_horiz')"
            size="22px"
          />
        </div>

        <div style="flex: 1; min-width: 0;">
          <div class="row items-center justify-between no-wrap">
            <span class="text-weight-bold text-caption ellipsis text-white">{{ item.type }}</span>
            <span
              class="text-weight-bolder text-subtitle2"
              :class="item.direction === 'credit' ? 'text-positive' : 'text-negative'"
            >
              {{ item.direction === 'credit' ? '+' : '-' }}₱{{ format(item.amount) }}
            </span>
          </div>

          <div class="row items-center justify-between text-caption q-mt-xs text-secondary" style="font-size: 0.72rem;">
            <span>Acc: {{ item.account_number }}</span>
            <span>{{ formatDate(item.date) }}</span>
          </div>

          <div v-if="item.reference" class="text-caption text-secondary ellipsis q-mt-xs" style="font-size: 0.68rem; font-family: monospace;">
            Ref: {{ item.reference }}
          </div>
        </div>
      </div>
    </div>

    <!-- Modern Data Table (Visible on Tablet and Desktop) -->
    <div v-if="rows.length > 0" class="gt-xs">
      <q-table
        :rows="rows"
        :columns="columns"
        row-key="key"
        :filter="filter"
        :loading="loading"
        flat
        bordered
        class="modern-data-table"
        :pagination="{ sortBy: 'date', descending: true, rowsPerPage: 15 }"
      >
        <template #body-cell-type="props">
          <q-td :props="props">
            <q-chip
              dense
              :color="badgeColor(props.row.type) === 'positive' ? 'green-1' : (badgeColor(props.row.type) === 'negative' ? 'red-1' : 'accent')"
              :text-color="badgeColor(props.row.type) === 'positive' ? 'positive' : (badgeColor(props.row.type) === 'negative' ? 'negative' : 'primary')"
              class="text-weight-bold"
              style="padding: 2px 10px; font-size: 0.72rem;"
            >
              {{ props.row.type }}
            </q-chip>
          </q-td>
        </template>

        <template #body-cell-reference="props">
          <q-td :props="props">
            <span class="text-caption text-weight-medium text-secondary" style="font-family: monospace;">
              {{ props.value || '—' }}
            </span>
          </q-td>
        </template>

        <template #body-cell-amount="props">
          <q-td :props="props" :class="props.row.direction === 'credit' ? 'text-positive text-weight-bolder' : 'text-negative text-weight-bolder'">
            {{ props.row.direction === 'credit' ? '+' : '-' }}₱{{ format(props.row.amount) }}
          </q-td>
        </template>
      </q-table>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

const auth = useAuthStore()
const rows = ref([])
const loading = ref(true)
const filter = ref('')

const filteredRows = computed(() => {
  if (!filter.value) return rows.value
  const q = filter.value.toLowerCase()
  return rows.value.filter((r) =>
    (r.account_number && String(r.account_number).toLowerCase().includes(q)) ||
    (r.type && r.type.toLowerCase().includes(q)) ||
    (r.reference && String(r.reference).toLowerCase().includes(q)),
  )
})

function formatDate (dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return Number.isNaN(d.getTime()) ? dateStr : d.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
}

const columns = [
  { name: 'account_number', label: 'Account Number', field: 'account_number', align: 'left' },
  { name: 'date', label: 'Date', field: 'date', align: 'left', sortable: true },
  { name: 'type', label: 'Transaction Type', field: 'type', align: 'left' },
  { name: 'reference', label: 'Reference Number', field: 'reference', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
]

function format (val) {
  return Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function badgeColor (type) {
  return {
    DEPOSIT: 'positive',
    WITHDRAWAL: 'negative',
    'TRANSFER OUT': 'negative',
    'TRANSFER IN': 'positive',
    INTERBANK: 'negative',
  }[type] || 'grey'
}

onMounted(async () => {
  try {
    const { data: allAccounts } = await api.get('/accounts/')
    const myAccountIds = allAccounts.filter((a) => a.customer_id === auth.userId).map((a) => a.id)
    const accountNumberById = Object.fromEntries(allAccounts.map((a) => [a.id, a.account_number]))

    const [deposits, withdrawals, transfers, interbank] = await Promise.all([
      api.get('/deposits/'),
      api.get('/withdrawals/'),
      api.get('/transfers/'),
      api.get('/interbank-transfers/'),
    ])

    const combined = []

    for (const d of deposits.data) {
      if (myAccountIds.includes(d.account_id)) {
        combined.push({
          key: `dep-${d.id}`,
          date: d.transaction_date,
          type: 'DEPOSIT',
          account_number: accountNumberById[d.account_id],
          reference: d.reference_number,
          amount: d.amount,
          direction: 'credit',
        })
      }
    }

    for (const w of withdrawals.data) {
      if (myAccountIds.includes(w.account_id)) {
        combined.push({
          key: `wd-${w.id}`,
          date: w.transaction_date,
          type: 'WITHDRAWAL',
          account_number: accountNumberById[w.account_id],
          reference: w.reference_number,
          amount: w.amount,
          direction: 'debit',
        })
      }
    }

    for (const t of transfers.data) {
      if (myAccountIds.includes(t.source_account_id)) {
        combined.push({
          key: `trf-out-${t.id}`,
          date: t.created_at,
          type: 'TRANSFER OUT',
          account_number: accountNumberById[t.source_account_id],
          reference: t.transfer_reference,
          amount: t.amount,
          direction: 'debit',
        })
      }
      if (myAccountIds.includes(t.destination_account_id)) {
        combined.push({
          key: `trf-in-${t.id}`,
          date: t.created_at,
          type: 'TRANSFER IN',
          account_number: accountNumberById[t.destination_account_id],
          reference: t.transfer_reference,
          amount: t.amount,
          direction: 'credit',
        })
      }
    }

    for (const i of interbank.data) {
      if (myAccountIds.includes(i.source_account_id)) {
        combined.push({
          key: `ibt-${i.id}`,
          date: i.initiated_at,
          type: 'INTERBANK',
          account_number: accountNumberById[i.source_account_id],
          reference: i.reference_number,
          amount: Number(i.amount) + Number(i.transfer_fee),
          direction: 'debit',
        })
      }
    }

    combined.sort((a, b) => new Date(b.date) - new Date(a.date))
    rows.value = combined
  } finally {
    loading.value = false
  }
})
</script>
