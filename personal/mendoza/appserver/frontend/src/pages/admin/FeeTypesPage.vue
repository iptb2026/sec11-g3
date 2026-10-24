<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Fee Types</div>
      <q-space />
      <q-btn
        color="primary"
        icon="add"
        label="New"
        @click="openCreate"
      />
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
      <q-card style="width: 420px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">
            {{ editingId ? 'Edit Fee Type' : 'New Fee Type' }}
          </div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="form.fee_code" label="Fee Code" filled />
          <q-input v-model="form.fee_name" label="Fee Name" filled />
          <q-input
            v-model="form.fee_description"
            label="Description"
            type="textarea"
            filled
          />
          <q-input
            v-model.number="form.fixed_amount"
            label="Fixed Amount"
            type="number"
            filled
          />
          <q-input
            v-model.number="form.percentage_rate"
            label="Percentage Rate %"
            type="number"
            filled
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup :disable="saving" />
          <q-btn
            color="primary"
            label="Save"
            :loading="saving"
            @click="save"
          />
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
          <strong>{{ selectedRow?.fee_name }}</strong>?
          This action cannot be undone.
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancel"
            :disable="deleting"
            @click="showDeleteDialog = false"
          />
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
