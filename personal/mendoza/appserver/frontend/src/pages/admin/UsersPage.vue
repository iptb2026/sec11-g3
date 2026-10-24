<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Users</div>
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

    <!-- Create / Edit User Dialog -->
    <q-dialog v-model="showDialog" persistent>
      <q-card style="width: 460px; max-width: 95vw">
        <q-card-section>
          <div class="text-h6">
            {{ editingId ? 'Edit User' : 'New User' }}
          </div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="form.username" label="Username" filled />
          <q-input
            v-model="form.password"
            label="Password"
            type="password"
            filled
            :hint="editingId ? 'Leave blank to keep the existing password, if supported by the backend' : 'Enter the user password'"
          />
          <q-input v-model="form.email" label="Email" filled />
          <q-input v-model="form.mobile_number" label="Mobile Number" filled />
          <q-input v-model="form.first_name" label="First Name" filled />
          <q-input v-model="form.middle_name" label="Middle Name" filled />
          <q-input v-model="form.last_name" label="Last Name" filled />
          <q-input
            v-model="form.date_of_birth"
            label="Date of Birth"
            filled
            hint="YYYY-MM-DD"
          />
          <q-select
            v-model="form.role_id"
            label="Role"
            filled
            emit-value
            map-options
            :options="roleOptions"
          />
          <q-input
            v-model="form.account_status"
            label="Account Status"
            filled
            hint="e.g. ACTIVE"
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
          Are you sure you want to delete user
          <strong>{{ selectedRow?.username }}</strong>?
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
  { name: 'username', label: 'Username', field: 'username', align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'first_name', label: 'First Name', field: 'first_name', align: 'left' },
  { name: 'last_name', label: 'Last Name', field: 'last_name', align: 'left' },
  { name: 'role_id', label: 'Role ID', field: 'role_id', align: 'left' },
  { name: 'account_status', label: 'Status', field: 'account_status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const roleOptions = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)

const showDialog = ref(false)
const showDeleteDialog = ref(false)
const editingId = ref(null)
const selectedRow = ref(null)

const emptyForm = () => ({
  username: '',
  password: '',
  email: '',
  mobile_number: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  date_of_birth: '',
  role_id: null,
  account_status: 'ACTIVE',
})

const form = ref(emptyForm())

async function loadRows () {
  loading.value = true

  try {
    const { data } = await api.get('/users/')
    rows.value = data
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Failed to load users',
    })
  } finally {
    loading.value = false
  }
}

async function loadRoleOptions () {
  try {
    const { data } = await api.get('/roles/')
    roleOptions.value = data.map((r) => ({
      label: `${r.role_code} - ${r.role_name}`,
      value: r.id,
    }))
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Failed to load roles',
    })
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
    username: row.username,
    password: '',
    email: row.email,
    mobile_number: row.mobile_number,
    first_name: row.first_name,
    middle_name: row.middle_name,
    last_name: row.last_name,
    date_of_birth: row.date_of_birth,
    role_id: row.role_id,
    account_status: row.account_status,
  }
  showDialog.value = true
}

async function save () {
  if (saving.value) return

  saving.value = true

  try {
    const payload = { ...form.value }

    // When editing, don't send an empty password.
    if (editingId.value && !payload.password) {
      delete payload.password
    }

    if (editingId.value) {
      await api.put(`/users/${editingId.value}`, payload)
    } else {
      await api.post('/users/', payload)
    }

    showDialog.value = false
    $q.notify({ type: 'positive', message: 'User saved successfully' })
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
    await api.delete(`/users/${selectedRow.value.id}`)

    showDeleteDialog.value = false
    $q.notify({ type: 'positive', message: 'User deleted successfully' })

    selectedRow.value = null
    await loadRows()
  } catch (err) {
    const status = err.response?.status
    let message = err.response?.data?.detail || 'Delete failed'

    if (status === 409) {
      message = 'This user is linked to other records and cannot be deleted.'
    } else if (status === 404) {
      message = 'User not found. Refreshing the list.'
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

onMounted(() => {
  loadRows()
  loadRoleOptions()
})
</script>
