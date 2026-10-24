<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Roles</div>
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

    <!-- Create / Edit Role Dialog -->
    <q-dialog v-model="showDialog" persistent>
      <q-card style="width: 400px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">
            {{ editingId ? 'Edit Role' : 'New Role' }}
          </div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="form.role_code" label="Role Code" filled />
          <q-input v-model="form.role_name" label="Role Name" filled />
          <q-input
            v-model="form.description"
            label="Description"
            type="textarea"
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

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="showDeleteDialog" persistent>
      <q-card style="width: 400px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">Confirm Delete</div>
        </q-card-section>

        <q-card-section>
          Are you sure you want to delete the role
          <strong>{{ selectedRow?.role_name }}</strong>?
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
  { name: 'role_code', label: 'Code', field: 'role_code', align: 'left' },
  { name: 'role_name', label: 'Name', field: 'role_name', align: 'left' },
  { name: 'description', label: 'Description', field: 'description', align: 'left' },
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
  role_code: '',
  role_name: '',
  description: '',
})

const form = ref(emptyForm())

async function loadRows () {
  loading.value = true

  try {
    const { data } = await api.get('/roles/')
    rows.value = data
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Failed to load roles',
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
    role_code: row.role_code,
    role_name: row.role_name,
    description: row.description,
  }
  showDialog.value = true
}

async function save () {
  if (saving.value) return

  saving.value = true

  try {
    if (editingId.value) {
      await api.put(`/roles/${editingId.value}`, form.value)
    } else {
      await api.post('/roles/', form.value)
    }

    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Role saved successfully' })
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
    await api.delete(`/roles/${selectedRow.value.id}`)

    showDeleteDialog.value = false
    $q.notify({ type: 'positive', message: 'Role deleted successfully' })

    selectedRow.value = null
    await loadRows()
  } catch (err) {
    const status = err.response?.status
    let message = err.response?.data?.detail || 'Delete failed'

    if (status === 409) {
      message = 'This role is assigned to users or referenced by other records and cannot be deleted.'
    } else if (status === 404) {
      message = 'Role not found. Refreshing the list.'
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
