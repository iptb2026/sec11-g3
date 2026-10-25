<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="sync_alt" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Interbank Transfers</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Records
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Manage outward fund transfers to external partner banking networks.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter interbank..."
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

        <q-btn
          color="primary"
          icon="add"
          label="New Interbank Transfer"
          class="text-weight-bold"
          unelevated
          @click="openCreate"
        />
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
      <template #body-cell-reference_number="props">
        <q-td :props="props">
          <span class="text-caption text-weight-medium" style="font-family: monospace; color: #FFFFFF;">
            {{ props.value || '—' }}
          </span>
        </q-td>
      </template>

      <template #body-cell-amount="props">
        <q-td :props="props" class="text-weight-bolder" style="color: #C50337;">
          ₱{{ formatMoney(props.value) }}
        </q-td>
      </template>

      <template #body-cell-transfer_fee="props">
        <q-td :props="props">
          ₱{{ formatMoney(props.value) }}
        </q-td>
      </template>

      <template #body-cell-status="props">
        <q-td :props="props">
          <q-badge
            :color="props.row.status === 'SUCCESS' ? 'positive' : (props.row.status === 'FAILED' ? 'negative' : 'warning')"
            class="text-weight-bold"
            style="padding: 4px 8px; font-size: 0.72rem;"
          >
            {{ props.row.status }}
          </q-badge>
        </q-td>
      </template>

      <template #body-cell-actions="props">
        <q-td :props="props" class="q-gutter-xs">
          <q-btn
            v-if="props.row.status === 'PROCESSING'"
            dense flat round icon="check_circle" color="positive"
            title="Mark SUCCESS"
            @click="markStatus(props.row, 'SUCCESS')"
          />
          <q-btn
            v-if="props.row.status === 'PROCESSING'"
            dense flat round icon="cancel" color="negative"
            title="Mark FAILED"
            @click="markStatus(props.row, 'FAILED')"
          />
          <q-btn dense flat round icon="edit" color="primary" @click="openEdit(props.row)" />
          <q-btn dense flat round icon="delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <!-- Create / Edit Dialog -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 460px; max-width: 95vw;" class="glass-card">
        <q-card-section class="row items-center bg-lavender-soft-gradient q-py-md">
          <q-avatar size="36px" color="primary" text-color="white" icon="sync_alt" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #FFFFFF;">
              {{ editingId ? 'Edit Interbank Transfer' : 'New Interbank Transfer' }}
            </div>
            <div class="text-caption text-grey-7">Transmit funds to external financial institution</div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md q-pt-md">
          <q-select
            v-model="form.source_account_id"
            label="Source Account"
            outlined
            emit-value
            map-options
            :options="accountOptions"
          />
          <q-select
            v-model="form.target_bank_id"
            label="Target Bank"
            outlined
            emit-value
            map-options
            :options="bankOptions"
          />
          <q-input v-model="form.target_account_number" label="Target Account Number" outlined />
          <q-input v-model="form.beneficiary_name" label="Beneficiary Name" outlined />
          <q-input v-model="form.reference_number" label="Reference Number" outlined />
          <q-input v-model.number="form.amount" label="Amount (PHP)" type="number" outlined />
          <q-input v-model.number="form.transfer_fee" label="Transfer Fee (PHP)" type="number" outlined />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup />
          <q-btn unelevated color="primary" label="Save Transfer" class="text-weight-bold" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()

function formatMoney (value) {
  const amount = Number(value)
  return Number.isFinite(amount)
    ? amount.toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    : value
}

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'source_account_id', label: 'Source Account ID', field: 'source_account_id', align: 'left' },
  { name: 'target_bank_id', label: 'Target Bank ID', field: 'target_bank_id', align: 'left' },
  { name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right', style: 'min-width: 150px; white-space: nowrap;', headerStyle: 'min-width: 150px; white-space: nowrap;' },
  { name: 'transfer_fee', label: 'Fee', field: 'transfer_fee', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left', style: 'min-width: 120px; white-space: nowrap;', headerStyle: 'min-width: 120px; white-space: nowrap;' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const filter = ref('')
const accountOptions = ref([])
const bankOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  source_account_id: null,
  target_bank_id: null,
  target_account_number: '',
  beneficiary_name: '',
  reference_number: '',
  amount: 0,
  transfer_fee: 0,
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/interbank-transfers/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const { data: accounts } = await api.get('/accounts/')
  accountOptions.value = accounts.map((a) => ({ label: a.account_number, value: a.id }))

  const { data: banks } = await api.get('/banks/')
  bankOptions.value = banks.map((b) => ({ label: `${b.bank_code} - ${b.bank_name}`, value: b.id }))
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    source_account_id: row.source_account_id,
    target_bank_id: row.target_bank_id,
    target_account_number: row.target_account_number,
    beneficiary_name: row.beneficiary_name,
    reference_number: row.reference_number,
    amount: Number(row.amount),
    transfer_fee: Number(row.transfer_fee),
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/interbank-transfers/${editingId.value}`, form.value)
    } else {
      await api.post('/interbank-transfers/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Interbank transfer saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

async function markStatus (row, status) {
  try {
    await api.put(`/interbank-transfers/${row.id}/status`, { status })
    $q.notify({ type: 'positive', message: `Marked ${status}` })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Status update failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    ok: { label: 'Delete', color: 'negative' },
    cancel: { label: 'Cancel', flat: true },
    message: `Delete interbank transfer "${row.reference_number}"?`,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/interbank-transfers/${row.id}`)
      $q.notify({ type: 'positive', message: 'Interbank transfer deleted' })
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
