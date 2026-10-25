<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="admin_panel_settings" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Access Roles</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Roles
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">System authorization levels, RBAC policies, and privilege assignments.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter roles..."
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
          label="New Role"
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
      <template #body-cell-role_code="props">
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

      <template #body-cell-role_name="props">
        <q-td :props="props">
          <span class="text-weight-bold" style="color: #FFFFFF;">{{ props.value }}</span>
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

    <!-- Create / Edit Role Dialog -->
    <q-dialog v-model="showDialog" persistent>
      <q-card style="width: 440px; max-width: 95vw;" class="glass-card">
        <q-card-section class="row items-center bg-lavender-soft-gradient q-py-md">
          <q-avatar size="36px" color="primary" text-color="white" icon="admin_panel_settings" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #FFFFFF;">
              {{ editingId ? 'Edit Role' : 'New Role' }}
            </div>
            <div class="text-caption text-grey-7">Define user access authorization scope</div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md q-pt-md">
          <q-input v-model="form.role_code" label="Role Code" outlined hint="e.g. ADMIN, STAFF, CUSTOMER" />
          <q-input v-model="form.role_name" label="Role Name" outlined />
          <q-input
            v-model="form.description"
            label="Description"
            type="textarea"
            outlined
            rows="3"
          />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup :disable="saving" />
          <q-btn
            unelevated
            color="primary"
            label="Save Role"
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
          Are you sure you want to delete the role
          <strong>{{ selectedRow?.role_name }}</strong>?
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
            label="Delete Role"
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
  { name: 'role_code', label: 'Code', field: 'role_code', align: 'left' },
  { name: 'role_name', label: 'Name', field: 'role_name', align: 'left' },
  { name: 'description', label: 'Description', field: 'description', align: 'left' },
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
