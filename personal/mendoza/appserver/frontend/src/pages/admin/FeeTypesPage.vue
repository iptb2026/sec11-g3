<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="sell" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Fee Types</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Types
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Configure transaction charges, account maintenance fees, and fixed penalties.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter fee types..."
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
          label="New Fee Type"
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
      <template #body-cell-fee_code="props">
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

      <template #body-cell-fee_name="props">
        <q-td :props="props">
          <span class="text-weight-bold" style="color: #FFFFFF;">{{ props.value }}</span>
        </q-td>
      </template>

      <template #body-cell-fixed_amount="props">
        <q-td :props="props" class="text-weight-medium">
          ₱{{ Number(props.value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </q-td>
      </template>

      <template #body-cell-percentage_rate="props">
        <q-td :props="props" class="text-weight-bold" style="color: #C50337;">
          {{ props.value }}%
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
            aria-label="Edit fee type"
            @click="openEdit(props.row)"
          />
          <q-btn
            dense
            flat
            round
            icon="delete"
            color="negative"
            aria-label="Delete fee type"
            @click="confirmDelete(props.row)"
          />
        </q-td>
      </template>
    </q-table>

    <!-- Create/Edit dialog -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 440px; max-width: 95vw;" class="glass-card">
        <q-card-section class="row items-center bg-lavender-soft-gradient q-py-md">
          <q-avatar size="36px" color="primary" text-color="white" icon="sell" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #FFFFFF;">
              {{ editingId ? 'Edit Fee Type' : 'New Fee Type' }}
            </div>
            <div class="text-caption text-grey-7">Define fee code, fixed amounts, and percentages</div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md q-pt-md">
          <q-input v-model="form.fee_code" label="Fee Code" outlined hint="e.g. ATM_WITHDRAWAL, OVERDRAFT" />
          <q-input v-model="form.fee_name" label="Fee Name" outlined />
          <q-input
            v-model="form.fee_description"
            label="Description"
            type="textarea"
            outlined
            rows="2"
          />
          <q-input
            v-model.number="form.fixed_amount"
            label="Fixed Amount (PHP)"
            type="number"
            outlined
          />
          <q-input
            v-model.number="form.percentage_rate"
            label="Percentage Rate %"
            type="number"
            outlined
          />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup :disable="saving" />
          <q-btn
            unelevated
            color="primary"
            label="Save Fee Type"
            class="text-weight-bold"
            :loading="saving"
            @click="save"
          />
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
          <strong>{{ selectedRow?.fee_name }}</strong>?
          This action cannot be undone.
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn
            flat
            label="Cancel"
            color="grey-8"
            :disable="deleting"
            @click="showDeleteDialog = false"
          />
          <q-btn
            unelevated
            color="negative"
            label="Delete Fee Type"
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
  { name: 'fee_code', label: 'Code', field: 'fee_code', align: 'left' },
  { name: 'fee_name', label: 'Name', field: 'fee_name', align: 'left' },
  {
    name: 'fixed_amount',
    label: 'Fixed Amount',
    field: 'fixed_amount',
    align: 'right',
  },
  {
    name: 'percentage_rate',
    label: 'Percentage %',
    field: 'percentage_rate',
    align: 'right',
  },
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
  fee_code: '',
  fee_name: '',
  fee_description: '',
  fixed_amount: 0,
  percentage_rate: 0,
})

const form = ref(emptyForm())

async function loadRows () {
  loading.value = true

  try {
    const { data } = await api.get('/fee-types/')
    rows.value = data
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Failed to load fee types',
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
    fee_code: row.fee_code,
    fee_name: row.fee_name,
    fee_description: row.fee_description || '',
    fixed_amount: Number(row.fixed_amount),
    percentage_rate: Number(row.percentage_rate),
  }
  showDialog.value = true
}

async function save () {
  if (saving.value) return

  saving.value = true

  try {
    if (editingId.value !== null) {
      await api.put(`/fee-types/${editingId.value}`, form.value)
    } else {
      await api.post('/fee-types/', form.value)
    }

    showDialog.value = false
    $q.notify({
      type: 'positive',
      message: 'Fee type saved successfully',
    })

    await loadRows()
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Failed to save fee type',
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
    await api.delete(`/fee-types/${selectedRow.value.id}`)

    showDeleteDialog.value = false
    $q.notify({
      type: 'positive',
      message: 'Fee type deleted successfully',
    })

    selectedRow.value = null
    await loadRows()
  } catch (err) {
    const status = err.response?.status
    let message = err.response?.data?.detail || 'Failed to delete fee type'

    if (status === 409) {
      message = 'This fee type is being used by another record and cannot be deleted.'
    } else if (status === 404) {
      message = 'This fee type was not found. Refreshing the list.'
      await loadRows()
    }

    $q.notify({
      type: 'negative',
      message,
    })
  } finally {
    deleting.value = false
  }
}

onMounted(loadRows)
</script>
