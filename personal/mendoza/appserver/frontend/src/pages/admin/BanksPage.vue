<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Banks</div>
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
            dense flat round icon="edit" color="primary"
            @click="openEdit(props.row)"
          />
          <q-btn
            dense flat round icon="delete" color="negative"
            @click="confirmDelete(props.row)"
          />
        </q-td>
      </template>
    </q-table>

    <!-- Create / Edit Bank Dialog -->
    <q-dialog v-model="showDialog" persistent>
      <q-card style="width: 420px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">
            {{ editingId ? 'Edit Bank' : 'New Bank' }}
          </div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="form.bank_code" label="Bank Code" filled />
          <q-input v-model="form.swift_code" label="SWIFT Code" filled />
          <q-input v-model="form.bank_name" label="Bank Name" filled />
          <q-input v-model="form.short_name" label="Short Name" filled />
          <q-input v-model="form.contact_email" label="Contact Email" filled />
          <q-select
            v-model="form.status"
            label="Status"
            filled
            :options="['ACTIVE', 'INACTIVE']"
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

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="showDeleteDialog" persistent>
      <q-card style="width: 400px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">Confirm Delete</div>
        </q-card-section>

        <q-card-section>
          Are you sure you want to delete bank
          <strong>{{ selectedRow?.bank_name }}</strong>?
          This action cannot be undone.
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            flat
            label="Cancel"
            color="grey"
            :disable="deleting"
            @click="showDeleteDialog = false"
          />
          <q-btn
            flat
            label="Delete"
            color="negative"
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
  { name: 'bank_code', label: 'Code', field: 'bank_code', align: 'left' },
  { name: 'bank_name', label: 'Name', field: 'bank_name', align: 'left' },
  { name: 'swift_code', label: 'SWIFT', field: 'swift_code', align: 'left' },
  { name: 'contact_email', label: 'Contact Email', field: 'contact_email', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
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
  bank_code: '',
  swift_code: '',
  bank_name: '',
  short_name: '',
  contact_email: '',
  status: 'ACTIVE',
})

const form = ref(emptyForm())

async function loadRows () {
  loading.value = true

  try {
    const { data } = await api.get('/banks/')
    rows.value = data
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Failed to load banks',
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
    bank_code: row.bank_code,
    swift_code: row.swift_code,
    bank_name: row.bank_name,
    short_name: row.short_name,
    contact_email: row.contact_email,
    status: row.status,
  }
  showDialog.value = true
}

async function save () {
  if (saving.value) return

  saving.value = true

  try {
    if (editingId.value) {
      await api.put(`/banks/${editingId.value}`, form.value)
    } else {
      await api.post('/banks/', form.value)
    }

    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Bank saved successfully' })
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
    await api.delete(`/banks/${selectedRow.value.id}`)

    showDeleteDialog.value = false
    $q.notify({
      type: 'positive',
      message: 'Bank deleted successfully',
    })

    selectedRow.value = null
    await loadRows()
  } catch (err) {
    const status = err.response?.status
    let message = err.response?.data?.detail || 'Delete failed'

    if (status === 409) {
      message = 'This bank is being used by other records and cannot be deleted.'
    } else if (status === 404) {
      message = 'Bank not found. Refreshing the list.'
      await loadRows()
    }

    $q.notify({
      type: 'negative',
      message: typeof message === 'string' ? message : JSON.stringify(message),
    })
  } finally {
    deleting.value = false
  }
}

onMounted(loadRows)
</script>
