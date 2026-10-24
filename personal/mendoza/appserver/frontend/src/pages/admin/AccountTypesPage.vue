<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Account Types</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table
      :rows="rows"
      :columns="columns"
      row-key="id"
      :loading="loading"
      flat
      bordered
    >
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            dense
            flat
            round
            icon="edit"
            color="primary"
            aria-label="Edit account type"
            @click="openEdit(props.row)"
          />
          <q-btn
            dense
            flat
            round
            icon="delete"
            color="negative"
            aria-label="Delete account type"
            @click="confirmDelete(props.row)"
          />
        </q-td>
      </template>
    </q-table>

    <!-- Create/Edit dialog -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 420px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">
            {{ editingId ? 'Edit Account Type' : 'New Account Type' }}
          </div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="form.type_code" label="Type Code" filled />
          <q-input v-model="form.type_name" label="Type Name" filled />
          <q-input
            v-model.number="form.minimum_balance"
            label="Minimum Balance"
            type="number"
            min="0"
            filled
          />
          <q-input
            v-model.number="form.opening_deposit"
            label="Opening Deposit"
            type="number"
            min="0"
            filled
          />
          <q-input
            v-model.number="form.annual_interest_rate"
            label="Annual Interest Rate %"
            type="number"
            min="0"
            filled
          />
          <q-input
            v-model.number="form.daily_withdrawal_limit"
            label="Daily Withdrawal Limit"
            type="number"
            min="0"
            filled
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" :loading="saving" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Delete confirmation dialog -->
    <q-dialog v-model="showDeleteDialog" persistent>
      <q-card style="width: 400px; max-width: 95vw">
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon name="warning" color="negative" size="md" />
          <div class="text-h6">Confirm Delete</div>
        </q-card-section>

        <q-card-section>
          Are you sure you want to delete
          <strong>{{ selectedRow?.type_name }}</strong>?
          This action cannot be undone.
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup :disable="deleting" />
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
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'type_code', label: 'Code', field: 'type_code', align: 'left' },
  { name: 'type_name', label: 'Name', field: 'type_name', align: 'left' },
  { name: 'minimum_balance', label: 'Min Balance', field: 'minimum_balance', align: 'right' },
  { name: 'opening_deposit', label: 'Opening Deposit', field: 'opening_deposit', align: 'right' },
  { name: 'annual_interest_rate', label: 'Annual Rate %', field: 'annual_interest_rate', align: 'right' },
  { name: 'daily_withdrawal_limit', label: 'Daily Limit', field: 'daily_withdrawal_limit', align: 'right' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const showDialog = ref(false)
const showDeleteDialog = ref(false)
const editingId = ref(null)
const selectedRow = ref(null)

const emptyForm = () => ({
  type_code: '',
  type_name: '',
  minimum_balance: 0,
  opening_deposit: 0,
  annual_interest_rate: 0,
  daily_withdrawal_limit: 0,
})

const form = ref(emptyForm())

async function loadRows () {
  loading.value = true

  try {
    const { data } = await api.get('/account-types/')
    rows.value = data
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Failed to load account types',
    })
  } finally {
    loading.value = false
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
    type_code: row.type_code,
    type_name: row.type_name,
    minimum_balance: Number(row.minimum_balance),
    opening_deposit: Number(row.opening_deposit),
    annual_interest_rate: Number(row.annual_interest_rate),
    daily_withdrawal_limit: Number(row.daily_withdrawal_limit),
  }
  showDialog.value = true
}

async function save () {
  if (saving.value) return

  saving.value = true

  try {
    if (editingId.value) {
      await api.put(`/account-types/${editingId.value}`, form.value)
    } else {
      await api.post('/account-types/', form.value)
    }

    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Account type saved successfully' })
    await loadRows()
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Save failed',
    })
  } finally {
    saving.value = false
  }
}

function confirmDelete (row) {
  selectedRow.value = row
  showDeleteDialog.value = true
}

async function deleteRow () {
  if (!selectedRow.value || deleting.value) return

  deleting.value = true

  try {
    await api.delete(`/account-types/${selectedRow.value.id}`)

    showDeleteDialog.value = false
    $q.notify({
      type: 'positive',
      message: 'Account type deleted successfully',
    })

    selectedRow.value = null
    await loadRows()
  } catch (err) {
    const status = err.response?.status
    let message = err.response?.data?.detail || 'Failed to delete account type'

    if (status === 409) {
      message = 'This account type is being used by an account and cannot be deleted.'
    } else if (status === 404) {
      message = 'This account type was not found. Refreshing the list.'
      await loadRows()
    }

    $q.notify({ type: 'negative', message })
  } finally {
    deleting.value = false
  }
}

onMounted(loadRows)
</script>
