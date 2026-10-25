<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="savings" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Interest Records</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Records
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Historical record of interest disbursements and credited yields.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter records..."
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
          label="New Record"
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
      <template #body-cell-amount_credited="props">
        <q-td :props="props" class="text-positive text-weight-bolder">
          +₱{{ Number(props.value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </q-td>
      </template>

      <template #body-cell-balance_before="props">
        <q-td :props="props">
          ₱{{ Number(props.value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </q-td>
      </template>

      <template #body-cell-balance_after="props">
        <q-td :props="props" class="text-weight-bold" style="color: #FFFFFF;">
          ₱{{ Number(props.value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </q-td>
      </template>

      <template #body-cell-actions="props">
        <q-td :props="props" class="q-gutter-xs">
          <q-btn dense flat round icon="delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <!-- Create Dialog -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 440px; max-width: 95vw;" class="glass-card">
        <q-card-section class="row items-center bg-lavender-soft-gradient q-py-md">
          <q-avatar size="36px" color="primary" text-color="white" icon="savings" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #FFFFFF;">New Interest Record</div>
            <div class="text-caption text-grey-7">Credit yield or interest disbursement to account</div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md q-pt-md">
          <q-select
            v-model="form.account_id"
            label="Account"
            outlined
            emit-value
            map-options
            :options="accountOptions"
          />
          <q-select
            v-model="form.policy_id"
            label="Interest Policy"
            outlined
            emit-value
            map-options
            :options="policyOptions"
          />
          <q-input v-model.number="form.amount_credited" label="Amount Credited (PHP)" type="number" outlined />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup />
          <q-btn unelevated color="primary" label="Save Record" class="text-weight-bold" @click="save" />
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
  { name: 'account_id', label: 'Account ID', field: 'account_id', align: 'left' },
  { name: 'policy_id', label: 'Policy ID', field: 'policy_id', align: 'left' },
  { name: 'amount_credited', label: 'Amount Credited', field: 'amount_credited', align: 'right' },
  { name: 'balance_before', label: 'Balance Before', field: 'balance_before', align: 'right' },
  { name: 'balance_after', label: 'Balance After', field: 'balance_after', align: 'right' },
  { name: 'credited_at', label: 'Credited At', field: 'credited_at', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const filter = ref('')
const accountOptions = ref([])
const policyOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const emptyForm = () => ({ account_id: null, policy_id: null, amount_credited: 0 })
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/interest-records/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const { data: accounts } = await api.get('/accounts/')
  accountOptions.value = accounts.map((a) => ({ label: a.account_number, value: a.id }))

  const { data: policies } = await api.get('/interest-policies/')
  policyOptions.value = policies.map((p) => ({ label: p.policy_name, value: p.id }))
}

function openCreate () {
  form.value = emptyForm()
  showDialog.value = true
}

async function save () {
  try {
    await api.post('/interest-records/', form.value)
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Interest record created' })
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
    message: `Delete interest record #${row.id}?`,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/interest-records/${row.id}`)
      $q.notify({ type: 'positive', message: 'Interest record deleted' })
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
