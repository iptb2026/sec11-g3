<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="account_box" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Accounts</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ groupedRows.length }} Accounts
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Customer checking, savings, and institutional banking accounts.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter accounts..."
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
          label="New Account"
          class="text-weight-bold"
          unelevated
          @click="openCreate"
        />
      </div>
    </div>

    <!-- Modern Data Table -->
    <q-table
      :rows="groupedRows"
      :columns="columns"
      :row-key="rowKey"
      :filter="filter"
      :loading="loading"
      flat
      bordered
      class="modern-data-table"
      :pagination="{ rowsPerPage: 15 }"
      :rows-per-page-options="[15, 30, 50, 0]"
    >
      <template v-slot:body="props">
        <q-tr :key="rowKey(props.row)" :props="props">
          <q-td v-for="col in props.cols" :key="col.name" :props="props">
            <template v-if="col.name === 'actions'">
              <div class="row items-center justify-end q-gutter-xs no-wrap">
                <q-btn dense flat round icon="edit" color="primary" size="sm" @click="openEdit(props.row)">
                  <q-tooltip>Edit Account</q-tooltip>
                </q-btn>
                <q-btn dense flat round icon="delete" color="negative" size="sm" @click="removeRow(props.row)">
                  <q-tooltip>Delete Account</q-tooltip>
                </q-btn>
              </div>
            </template>
            <template v-else-if="col.name === 'account_number'">
              <span class="text-weight-bold" style="font-family: monospace; color: #FFFFFF;">
                {{ col.value }}
              </span>
            </template>
            <template v-else-if="col.name === 'available_balance'">
              <span class="text-weight-bolder text-positive">
                ₱{{ Number(col.value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
              </span>
            </template>
            <template v-else-if="col.name === 'ledger_balance'">
              <span class="text-weight-medium" style="color: #C50337;">
                ₱{{ Number(col.value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
              </span>
            </template>
            <template v-else-if="col.name === 'status'">
              <q-badge
                :color="col.value === 'ACTIVE' ? 'positive' : 'grey-7'"
                class="text-weight-bold"
                style="padding: 4px 8px; font-size: 0.72rem;"
              >
                {{ col.value }}
              </q-badge>
            </template>
            <template v-else>{{ col.value }}</template>
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <!-- Create / Edit Dialog -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 460px; max-width: 95vw;" class="glass-card">
        <q-card-section class="row items-center bg-lavender-soft-gradient q-py-md">
          <q-avatar size="36px" color="primary" text-color="white" icon="account_box" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #FFFFFF;">
              {{ editingId ? 'Edit Account' : 'New Account' }}
            </div>
            <div class="text-caption text-grey-7">Configure customer banking account settings</div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md q-pt-md">
          <q-input v-model="form.account_number" label="Account Number" outlined />
          <q-select
            v-model="form.customer_id"
            label="Customer"
            outlined
            emit-value
            map-options
            :options="customerOptions"
          />
          <q-select
            v-model="form.account_type_id"
            label="Account Type"
            outlined
            emit-value
            map-options
            :options="accountTypeOptions"
          />
          <q-input v-model="form.currency_code" label="Currency Code" outlined />
          <q-input v-model="form.branch_code" label="Branch Code" outlined />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup />
          <q-btn unelevated color="primary" label="Save Account" class="text-weight-bold" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Confirm Delete Dialog -->
    <q-dialog v-model="showDeleteDialog" persistent>
      <q-card style="min-width: 320px; max-width: 440px;" class="glass-card">
        <q-card-section class="row items-center bg-red-1 q-py-md">
          <q-avatar size="36px" color="negative" text-color="white" icon="warning" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #991B1B;">Confirm Delete</div>
            <div class="text-caption text-red-9">Irreversible action</div>
          </div>
        </q-card-section>

        <q-card-section class="q-pt-md">
          Are you sure you want to delete account
          <strong>{{ selectedRow?.account_number }}</strong>?
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup />
          <q-btn
            unelevated
            color="negative"
            label="Delete Account"
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
const filter = ref('')
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
