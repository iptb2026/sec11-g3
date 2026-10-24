<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Accounts</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table
      :rows="groupedRows"
      :columns="columns"
      :row-key="rowKey"
      :loading="loading"
      flat
      bordered
      :pagination="{ rowsPerPage: 0 }"
      :rows-per-page-options="[0]"
    >
      <template v-slot:body="props">
        <q-tr :key="rowKey(props.row)" :props="props">
          <q-td v-for="col in props.cols" :key="col.name" :props="props">
            <template v-if="col.name === 'actions'">
              <q-btn dense flat round icon="edit" color="primary" @click="openEdit(props.row)" />
              <q-btn dense flat round icon="delete" color="negative" @click="removeRow(props.row)" />
            </template>
            <template v-else>{{ col.value }}</template>
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 440px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit Account' : 'New Account' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="form.account_number" label="Account Number" filled />
          <q-select
            v-model="form.customer_id"
            label="Customer"
            filled
            emit-value
            map-options
            :options="customerOptions"
          />
          <q-select
            v-model="form.account_type_id"
            label="Account Type"
            filled
            emit-value
            map-options
            :options="accountTypeOptions"
          />
          <q-input v-model="form.currency_code" label="Currency Code" filled />
          <q-input v-model="form.branch_code" label="Branch Code" filled />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="showDeleteDialog" persistent>
      <q-card style="min-width: 320px; max-width: 440px">
        <q-card-section>
          <div class="text-h6">Confirm Delete</div>
        </q-card-section>

        <q-card-section>
          Are you sure you want to delete account
          <strong>{{ selectedRow?.account_number }}</strong>?
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="negative"
            label="Delete"
            :loading="deleting"
            @click="deleteRow"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_number', label: 'Account #', field: 'account_number', align: 'left' },
  { name: 'customer_id', label: 'Customer', field: 'customer_name', align: 'left' },
  { name: 'account_type_id', label: 'Type ID', field: 'account_type_id', align: 'left' },
  { name: 'available_balance', label: 'Available Balance', field: 'available_balance', align: 'right' },
  { name: 'ledger_balance', label: 'Ledger Balance', field: 'ledger_balance', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const customerOptions = ref([])
const accountTypeOptions = ref([])
const customerNameById = ref({})
const loading = ref(false)

function rowKey (row) {
  return `account-${row.id}`
}

const groupedRows = computed(() => {
  const uniqueRows = rows.value.filter(
    (row, index, allRows) =>
      allRows.findIndex(item => String(item.id) === String(row.id)) === index
  )

  return uniqueRows
    .sort((a, b) => Number(b.id || 0) - Number(a.id || 0))
    .map(row => ({
      ...row,
      customer_name:
        customerNameById.value[Number(row.customer_id)] ||
        row.customer_name ||
        row.customer?.full_name ||
        row.customer?.name ||
        (row.customer_id != null
          ? `Customer #${row.customer_id}`
          : 'Unknown Customer'),
    }))
})
const showDialog = ref(false)
const showDeleteDialog = ref(false)
const selectedRow = ref(null)
const deleting = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  account_number: '',
  customer_id: null,
  account_type_id: null,
  currency_code: 'PHP',
  branch_code: '',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/accounts/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const { data: users } = await api.get('/users/')
  customerOptions.value = users.map((u) => ({ label: `${u.username} (${u.first_name} ${u.last_name})`, value: u.id }))
  customerNameById.value = Object.fromEntries(users.map((u) => [Number(u.id), `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.username || `Customer #${u.id}`]))

  const { data: types } = await api.get('/account-types/')
  accountTypeOptions.value = types.map((t) => ({ label: `${t.type_code} - ${t.type_name}`, value: t.id }))
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_number: row.account_number,
    customer_id: row.customer_id,
    account_type_id: row.account_type_id,
    currency_code: row.currency_code,
    branch_code: row.branch_code,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/accounts/${editingId.value}`, form.value)
    } else {
      await api.post('/accounts/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Account saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  selectedRow.value = row
  showDeleteDialog.value = true
}

async function deleteRow () {
  if (!selectedRow.value || deleting.value) return

  deleting.value = true
  try {
    await api.delete(`/accounts/${selectedRow.value.id}`)
    showDeleteDialog.value = false
    $q.notify({ type: 'positive', message: 'Account deleted' })
    selectedRow.value = null
    await loadRows()
  } catch (err) {
    console.error('Account deletion failed:', {
      status: err.response?.status,
      data: err.response?.data,
      message: err.message
    })
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || err.message || 'Delete failed',
      timeout: 6000
    })
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadRows()
  loadOptions()
})
</script>
