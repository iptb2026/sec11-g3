<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="category" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Account Types</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Types
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Configure account tiers, minimum balances, and interest terms.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter account types..."
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
          label="New Type"
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
      <template #body-cell-type_code="props">
        <q-td :props="props">
          <q-chip
            dense
            color="accent"
            text-color="primary"
            class="text-weight-bold"
            style="font-family: monospace; font-size: 0.75rem;"
          >
            {{ props.value }}
          </q-chip>
        </q-td>
      </template>

      <template #body-cell-type_name="props">
        <q-td :props="props">
          <span class="text-weight-bold" style="color: #FFFFFF;">{{ props.value }}</span>
        </q-td>
      </template>

      <template #body-cell-minimum_balance="props">
        <q-td :props="props">
          ₱{{ Number(props.value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </q-td>
      </template>

      <template #body-cell-opening_deposit="props">
        <q-td :props="props">
          ₱{{ Number(props.value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </q-td>
      </template>

      <template #body-cell-annual_interest_rate="props">
        <q-td :props="props" class="text-positive text-weight-bold">
          {{ props.value }}%
        </q-td>
      </template>

      <template #body-cell-daily_withdrawal_limit="props">
        <q-td :props="props" class="text-weight-bold" style="color: #C50337;">
          ₱{{ Number(props.value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </q-td>
      </template>

      <template #body-cell-actions="props">
        <q-td :props="props" class="q-gutter-xs">
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
      <q-card style="width: 440px; max-width: 95vw;" class="glass-card">
        <q-card-section class="row items-center bg-lavender-soft-gradient q-py-md">
          <q-avatar size="36px" color="primary" text-color="white" icon="category" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #FFFFFF;">
              {{ editingId ? 'Edit Account Type' : 'New Account Type' }}
            </div>
            <div class="text-caption text-grey-7">Define tier requirements, minimum balances, and interest rates</div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md q-pt-md">
          <q-input v-model="form.type_code" label="Type Code" outlined hint="e.g. SAVINGS, CHECKING" />
          <q-input v-model="form.type_name" label="Type Name" outlined />
          <q-input
            v-model.number="form.minimum_balance"
            label="Minimum Balance (PHP)"
            type="number"
            min="0"
            outlined
          />
          <q-input
            v-model.number="form.opening_deposit"
            label="Opening Deposit (PHP)"
            type="number"
            min="0"
            outlined
          />
          <q-input
            v-model.number="form.annual_interest_rate"
            label="Annual Interest Rate %"
            type="number"
            min="0"
            outlined
          />
          <q-input
            v-model.number="form.daily_withdrawal_limit"
            label="Daily Withdrawal Limit (PHP)"
            type="number"
            min="0"
            outlined
          />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup />
          <q-btn unelevated color="primary" label="Save Type" class="text-weight-bold" :loading="saving" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Delete confirmation dialog -->
    <q-dialog v-model="showDeleteDialog" persistent>
      <q-card style="width: 400px; max-width: 95vw;" class="glass-card">
        <q-card-section class="row items-center bg-red-1 q-py-md">
          <q-avatar size="36px" color="negative" text-color="white" icon="warning" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #991B1B;">Confirm Delete</div>
            <div class="text-caption text-red-9">Irreversible action</div>
          </div>
        </q-card-section>

        <q-card-section class="q-pt-md">
          Are you sure you want to delete
          <strong>{{ selectedRow?.type_name }}</strong>?
          This action cannot be undone.
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup :disable="deleting" />
          <q-btn
            unelevated
            color="negative"
            label="Delete Type"
            class="text-weight-bold"
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
const filter = ref('')
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
