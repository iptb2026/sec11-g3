<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="swap_horiz" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Internal Transfers</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Records
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Manage book-to-book account fund transfers and ledger movements.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter transfers..."
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
          label="New Transfer"
          class="text-weight-bold"
          unelevated
          @click="openCreate"
        />
      </div>
    </div>

    <!-- Modern Data Table -->
    <q-table
      :rows="rows"
      :columns="columns"
      row-key="id"
      :filter="filter"
      :loading="loading"
      flat
      bordered
      class="modern-data-table"
      :pagination="{ rowsPerPage: 10 }"
    >
      <template #body-cell-transfer_reference="props">
        <q-td :props="props">
          <span class="text-caption text-weight-medium" style="font-family: monospace; color: #FFFFFF;">
            {{ props.value || '—' }}
          </span>
        </q-td>
      </template>

      <template #body-cell-amount="props">
        <q-td :props="props" class="text-weight-bolder" style="color: #C50337;">
          ₱{{ Number(props.value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </q-td>
      </template>

      <template #body-cell-status="props">
        <q-td :props="props">
          <q-badge
            :color="props.value === 'COMPLETED' || props.value === 'SUCCESS' ? 'positive' : (props.value === 'FAILED' ? 'negative' : 'warning')"
            class="text-weight-bold"
            style="padding: 4px 8px; font-size: 0.72rem;"
          >
            {{ props.value || 'PENDING' }}
          </q-badge>
        </q-td>
      </template>
    </q-table>

    <!-- Create Dialog -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 460px; max-width: 95vw;" class="glass-card">
        <q-card-section class="row items-center bg-lavender-soft-gradient q-py-md">
          <q-avatar size="36px" color="primary" text-color="white" icon="swap_horiz" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #FFFFFF;">New Account Transfer</div>
            <div class="text-caption text-grey-7">Transfer funds between internal bank accounts</div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md q-pt-md">
          <q-select
            v-model="form.source_account_id"
            label="Source Account (Debit)"
            outlined
            emit-value
            map-options
            :options="accountOptions"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label class="text-weight-bold">{{ scope.opt.label }}</q-item-label>
                  <q-item-label caption>{{ scope.opt.holder }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>

          <q-select
            v-model="form.destination_account_id"
            label="Destination Account (Credit)"
            outlined
            emit-value
            map-options
            :options="accountOptions"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label class="text-weight-bold">{{ scope.opt.label }}</q-item-label>
                  <q-item-label caption>{{ scope.opt.holder }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>

          <q-input v-model="form.transfer_reference" label="Transfer Reference" outlined />
          <q-input v-model.number="form.amount" label="Amount (PHP)" type="number" outlined />
          <q-input v-model="form.transfer_type" label="Transfer Type" outlined />
          <q-input v-model="form.remarks" label="Remarks" type="textarea" outlined rows="2" />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup />
          <q-btn unelevated color="primary" label="Save Transfer" class="text-weight-bold" @click="save" />
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
  { name: 'source_account_id', label: 'From Account ID', field: 'source_account_id', align: 'left' },
  { name: 'destination_account_id', label: 'To Account ID', field: 'destination_account_id', align: 'left' },
  { name: 'transfer_reference', label: 'Reference', field: 'transfer_reference', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
]

const rows = ref([])
const filter = ref('')
const accountOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const emptyForm = () => ({
  source_account_id: null,
  destination_account_id: null,
  transfer_reference: '',
  amount: 0,
  transfer_type: 'INTERNAL',
  remarks: '',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/transfers/')
  rows.value = data
  loading.value = false
}

async function loadOptions () {
  const [{ data: accounts }, { data: users }] = await Promise.all([
    api.get('/accounts/'),
    api.get('/users/'),
  ])

  const nameByUserId = {}
  users.forEach((u) => {
    nameByUserId[u.id] = `${u.first_name} ${u.last_name}`
  })

  accountOptions.value = accounts.map((a) => ({
    label: a.account_number,
    value: a.id,
    holder: nameByUserId[a.customer_id] || '',
  }))
}

function openCreate () {
  form.value = emptyForm()
  showDialog.value = true
}


async function save () {
  try {
    await api.post('/transfers/', form.value)
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Transfer recorded' })
    await loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}



onMounted(() => {
  loadRows()
  loadOptions()
})
</script>
