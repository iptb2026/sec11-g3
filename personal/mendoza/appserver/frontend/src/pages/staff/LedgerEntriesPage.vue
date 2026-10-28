<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="menu_book" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Ledger Entries</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Entries
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Transaction-generated ledger entries are read-only; corrections must use a reversal.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter ledger..."
          class="bg-white"
          style="min-width: 200px;"
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

    <!-- Modern Data Table -->
    <q-table
      class="modern-data-table"
      :rows="rows"
      :columns="columns"
      row-key="id"
      :filter="filter"
      :loading="loading"
      flat
      bordered
      :pagination="{ rowsPerPage: 10 }"
    >
      <template #body-cell-transaction_reference="props">
        <q-td :props="props">
          <span class="text-caption text-weight-medium" style="font-family: monospace; color: #FFFFFF;">
            {{ props.value || '—' }}
          </span>
        </q-td>
      </template>

      <template #body-cell-debit_amount="props">
        <q-td :props="props" class="text-negative text-weight-bold">
          <span v-if="Number(props.value) > 0">-₱{{ Number(props.value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
          <span v-else class="text-grey-5">—</span>
        </q-td>
      </template>

      <template #body-cell-credit_amount="props">
        <q-td :props="props" class="text-positive text-weight-bold">
          <span v-if="Number(props.value) > 0">+₱{{ Number(props.value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
          <span v-else class="text-grey-5">—</span>
        </q-td>
      </template>

      <template #body-cell-balance_after="props">
        <q-td :props="props" class="text-weight-bolder" style="color: #FFFFFF;">
          ₱{{ Number(props.value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </q-td>
      </template>

    </q-table>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_id', label: 'Account ID', field: 'account_id', align: 'left' },
  { name: 'transaction_reference', label: 'Reference', field: 'transaction_reference', align: 'left' },
  { name: 'transaction_type', label: 'Type', field: 'transaction_type', align: 'left' },
  { name: 'debit_amount', label: 'Debit', field: 'debit_amount', align: 'right' },
  { name: 'credit_amount', label: 'Credit', field: 'credit_amount', align: 'right' },
  { name: 'balance_after', label: 'Balance After', field: 'balance_after', align: 'right' },
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left' },
]

const rows = ref([])
const filter = ref('')
const accountOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const emptyForm = () => ({ account_id: null, transaction_reference: '', transaction_type: '', debit_amount: 0, credit_amount: 0 })
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/ledger-entries/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const { data } = await api.get('/accounts/')
  accountOptions.value = data.map((a) => ({ label: a.account_number, value: a.id }))
}

function openCreate () {
  form.value = emptyForm()
  showDialog.value = true
}

async function save () {
  try {
    await api.post('/ledger-entries/', form.value)
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Ledger entry created' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    ok: { label: 'Delete', color: 'negative' },
    cancel: { label: 'Cancel', flat: true },
    message: `Delete ledger entry #${row.id}?`,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/ledger-entries/${row.id}`)
      $q.notify({ type: 'positive', message: 'Ledger entry deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(() => {
  loadRows()
  loadOptions()
})
</script>
