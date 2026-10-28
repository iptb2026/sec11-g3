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
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Fee Records</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Records
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Historical fee records are read-only to preserve their linked account balances.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter fees..."
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

      <template #body-cell-amount_charged="props">
        <q-td :props="props" class="text-negative text-weight-bolder">
          ₱{{ Number(props.value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
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
  { name: 'fee_type_id', label: 'Fee Type ID', field: 'fee_type_id', align: 'left' },
  { name: 'transaction_reference', label: 'Reference', field: 'transaction_reference', align: 'left' },
  { name: 'amount_charged', label: 'Amount Charged', field: 'amount_charged', align: 'right' },
  { name: 'charged_at', label: 'Charged At', field: 'charged_at', align: 'left' },
]

const rows = ref([])
const filter = ref('')
const accountOptions = ref([])
const feeTypeOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  account_id: null,
  fee_type_id: null,
  transaction_reference: '',
  amount_charged: 0,
  remarks: '',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/fee-records/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Failed to load fee records' })
  } finally {
    loading.value = false
  }
}

async function loadOptions () {
  try {
    const { data: accounts } = await api.get('/accounts/')
    accountOptions.value = accounts.map((a) => ({ label: a.account_number, value: a.id }))

    const { data: feeTypes } = await api.get('/fee-types/')
    feeTypeOptions.value = feeTypes.map((f) => ({ label: `${f.fee_code} - ${f.fee_name}`, value: f.id }))
  } catch (err) {
    console.error('Failed to load fee options:', err)
  }
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_id: row.account_id,
    fee_type_id: row.fee_type_id,
    transaction_reference: row.transaction_reference,
    amount_charged: Number(row.amount_charged),
    remarks: row.remarks,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/fee-records/${editingId.value}`, form.value)
    } else {
      await api.post('/fee-records/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Fee record saved' })
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
    message: `Delete fee record #${row.id}?`,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/fee-records/${row.id}`)
      $q.notify({ type: 'positive', message: 'Fee record deleted' })
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
