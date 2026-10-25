<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="people" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">System Users</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Accounts
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Manage customer accounts, teller staff credentials, and admin privileges.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter users..."
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
          label="New User"
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
      <template #body-cell-username="props">
        <q-td :props="props">
          <div class="row items-center no-wrap">
            <q-avatar size="28px" color="accent" text-color="primary" class="text-weight-bold q-mr-sm" style="font-size: 0.75rem;">
              {{ (props.value || 'U').charAt(0).toUpperCase() }}
            </q-avatar>
            <span class="text-weight-bold" style="color: #FFFFFF;">{{ props.value }}</span>
          </div>
        </q-td>
      </template>

      <template #body-cell-account_status="props">
        <q-td :props="props">
          <q-badge
            :color="props.value === 'ACTIVE' ? 'positive' : 'grey-7'"
            class="text-weight-bold"
            style="padding: 4px 8px; font-size: 0.72rem;"
          >
            {{ props.value || 'ACTIVE' }}
          </q-badge>
        </q-td>
      </template>

      <template #body-cell-actions="props">
        <q-td :props="props" class="q-gutter-xs">
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
      <q-card style="width: 480px; max-width: 95vw;" class="glass-card">
        <q-card-section class="row items-center bg-lavender-soft-gradient q-py-md">
          <q-avatar size="36px" color="primary" text-color="white" icon="person_add" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #FFFFFF;">
              {{ editingId ? 'Edit User' : 'New User' }}
            </div>
            <div class="text-caption text-grey-7">Configure user account credentials and role</div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md q-pt-md" style="max-height: 70vh; overflow-y: auto;">
          <q-input v-model="form.username" label="Username" outlined />
          <q-input
            v-model="form.password"
            label="Password"
            type="password"
            outlined
            :hint="editingId ? 'Leave blank to keep the existing password, if supported by the backend' : 'Enter the user password'"
          />
          <q-input v-model="form.email" label="Email Address" outlined />
          <q-input v-model="form.mobile_number" label="Mobile Number" outlined />
          <div class="row q-col-gutter-sm">
            <div class="col-6">
              <q-input v-model="form.first_name" label="First Name" outlined />
            </div>
            <div class="col-6">
              <q-input v-model="form.last_name" label="Last Name" outlined />
            </div>
          </div>
          <q-input v-model="form.middle_name" label="Middle Name (Optional)" outlined />
          <q-input
            v-model="form.date_of_birth"
            label="Date of Birth"
            outlined
            hint="YYYY-MM-DD"
          />
          <q-select
            v-model="form.role_id"
            label="Role"
            outlined
            emit-value
            map-options
            :options="roleOptions"
          />
          <q-select
            v-model="form.account_status"
            label="Account Status"
            outlined
            :options="['ACTIVE', 'LOCKED', 'DISABLED']"
          />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup :disable="saving" />
          <q-btn
            unelevated
            color="primary"
            label="Save User"
            class="text-weight-bold"
            :loading="saving"
            @click="save"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Delete Confirmation Dialog -->
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
          Are you sure you want to delete user
          <strong>{{ selectedRow?.username }}</strong>?
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
            label="Delete User"
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
import { useAuthStore } from '@/stores/auth-store'

const $q = useQuasar()
const auth = useAuthStore()

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
const filter = ref('')
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
    if (!payload.password || !payload.password.trim()) {
      delete payload.password
    } else {
      payload.password = payload.password.trim()
    }

    // Clean up empty optional fields so backend gets null instead of invalid empty strings
    if (!payload.email || !payload.email.trim()) {
      payload.email = null
    } else {
      payload.email = payload.email.trim()
    }

    if (!payload.mobile_number || !payload.mobile_number.trim()) {
      payload.mobile_number = null
    } else {
      payload.mobile_number = payload.mobile_number.trim()
    }

    if (!payload.middle_name || !payload.middle_name.trim()) {
      payload.middle_name = null
    } else {
      payload.middle_name = payload.middle_name.trim()
    }

    if (!payload.date_of_birth || !payload.date_of_birth.trim()) {
      payload.date_of_birth = null
    } else {
      payload.date_of_birth = payload.date_of_birth.trim()
    }

    if (payload.first_name) payload.first_name = payload.first_name.trim()
    if (payload.last_name) payload.last_name = payload.last_name.trim()
    if (payload.username) payload.username = payload.username.trim()

    if (editingId.value) {
      await api.put(`/users/${editingId.value}`, payload)

      // If user edited their own details, update the auth store
      if (auth.userId === editingId.value) {
        if (payload.username) auth.username = payload.username
        if (payload.first_name) auth.firstName = payload.first_name
        if (payload.last_name) auth.lastName = payload.last_name
        if (payload.role_id) {
          auth.roleId = payload.role_id
          const selectedRole = roleOptions.value.find((r) => r.value === payload.role_id)
          if (selectedRole) {
            auth.roleName = selectedRole.label.split(' - ')[1] || auth.roleName
          }
        }
        auth.persist()
      }
    } else {
      await api.post('/users/', payload)
    }

    showDialog.value = false
    $q.notify({ type: 'positive', message: 'User saved successfully' })
    await loadRows()
  } catch (err) {
    const detail = err.response?.data?.detail
    const msg = Array.isArray(detail)
      ? detail.map((d) => d.msg || `${d.loc?.slice(-1)[0]}: ${d.type}`).join(', ')
      : (detail || 'Save failed')
    $q.notify({
      type: 'negative',
      message: msg,
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
