<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="percent" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Interest Policies</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Policies
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Configure annual percentage yield, compounding intervals, and maturity dates.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter policies..."
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
          label="New Policy"
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
      <template #body-cell-annual_rate="props">
        <q-td :props="props" class="text-weight-bolder text-positive">
          {{ props.value }}%
        </q-td>
      </template>

      <template #body-cell-actions="props">
        <q-td :props="props" class="q-gutter-xs">
          <q-btn dense flat round icon="edit" color="primary" @click="openEdit(props.row)" />
          <q-btn dense flat round icon="delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <!-- Create / Edit Dialog -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 440px; max-width: 95vw;" class="glass-card">
        <q-card-section class="row items-center bg-lavender-soft-gradient q-py-md">
          <q-avatar size="36px" color="primary" text-color="white" icon="percent" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #FFFFFF;">
              {{ editingId ? 'Edit Interest Policy' : 'New Interest Policy' }}
            </div>
            <div class="text-caption text-grey-7">Define yield rates and calculation cycles</div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md q-pt-md">
          <q-select
            v-model="form.account_type_id"
            label="Account Type"
            outlined
            emit-value
            map-options
            :options="accountTypeOptions"
          />
          <q-input v-model="form.policy_name" label="Policy Name" outlined />
          <q-input v-model.number="form.annual_rate" label="Annual Rate (%)" type="number" outlined />
          <q-input v-model="form.compounding_frequency" label="Compounding Frequency" outlined hint="e.g. MONTHLY" />
          <q-input v-model="form.effective_date" label="Effective Date" outlined hint="YYYY-MM-DD" />
          <q-input v-model="form.expiration_date" label="Expiration Date" outlined hint="YYYY-MM-DD" />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup />
          <q-btn unelevated color="primary" label="Save Policy" class="text-weight-bold" @click="save" />
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
  { name: 'account_type_id', label: 'Account Type ID', field: 'account_type_id', align: 'left' },
  { name: 'policy_name', label: 'Policy Name', field: 'policy_name', align: 'left' },
  { name: 'annual_rate', label: 'Annual Rate %', field: 'annual_rate', align: 'right' },
  { name: 'compounding_frequency', label: 'Compounding', field: 'compounding_frequency', align: 'left' },
  { name: 'effective_date', label: 'Effective', field: 'effective_date', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const filter = ref('')
const accountTypeOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  account_type_id: null,
  policy_name: '',
  annual_rate: 0,
  compounding_frequency: '',
  effective_date: '',
  expiration_date: '',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/interest-policies/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const { data } = await api.get('/account-types/')
  accountTypeOptions.value = data.map((t) => ({ label: `${t.type_code} - ${t.type_name}`, value: t.id }))
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_type_id: row.account_type_id,
    policy_name: row.policy_name,
    annual_rate: Number(row.annual_rate),
    compounding_frequency: row.compounding_frequency,
    effective_date: row.effective_date,
    expiration_date: row.expiration_date,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/interest-policies/${editingId.value}`, form.value)
    } else {
      await api.post('/interest-policies/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Interest policy saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    ok: { label: 'Delete', color: 'negative' },
    cancel: { label: 'Cancel', flat: true },
    message: `Delete interest policy "${row.policy_name}"?`,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/interest-policies/${row.id}`)
      $q.notify({ type: 'positive', message: 'Interest policy deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Delete failed' })
    }
  })
}

onMounted(() => {
  loadRows()
  loadOptions()
})
</script>
