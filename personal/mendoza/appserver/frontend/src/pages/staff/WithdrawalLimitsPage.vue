<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="speed" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Withdrawal Limits</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Policies
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Threshold controls and daily maximum withdrawal constraints per account.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter limits..."
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
          label="New Limit"
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
      <template #body-cell-daily_limit_amount="props">
        <q-td :props="props" class="text-weight-bolder" style="color: #FFFFFF;">
          ₱{{ Number(props.value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </q-td>
      </template>

      <template #body-cell-daily_used_amount="props">
        <q-td :props="props" class="text-negative text-weight-bold">
          ₱{{ Number(props.value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
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
          <q-avatar size="36px" color="primary" text-color="white" icon="speed" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #FFFFFF;">
              {{ editingId ? 'Edit Withdrawal Limit' : 'New Withdrawal Limit' }}
            </div>
            <div class="text-caption text-grey-7">Set daily cap and threshold policies</div>
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

          <q-input
            v-if="form.account_id"
            :model-value="accountHolderName"
            label="Account Holder"
            outlined
            readonly
            class="bg-grey-1"
          />

          <q-input v-model.number="form.daily_limit_amount" label="Daily Limit Amount (PHP)" type="number" outlined />
          <q-input v-model="form.last_reset_date" label="Last Reset Date" outlined hint="YYYY-MM-DD" />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup />
          <q-btn unelevated color="primary" label="Save Limit" class="text-weight-bold" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar, Dialog } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_id', label: 'Account ID', field: 'account_id', align: 'left' },
  { name: 'daily_limit_amount', label: 'Daily Limit', field: 'daily_limit_amount', align: 'right' },
  { name: 'daily_used_amount', label: 'Used Today', field: 'daily_used_amount', align: 'right' },
  { name: 'last_reset_date', label: 'Last Reset', field: 'last_reset_date', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const filter = ref('')
const accountOptions = ref([])
const accountHolderByAccountId = ref({})
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({ account_id: null, daily_limit_amount: 0, last_reset_date: '' })
const form = ref(emptyForm())

const accountHolderName = computed(() => accountHolderByAccountId.value[form.value.account_id] || '')

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/withdrawal-limits/')
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
  accountHolderByAccountId.value = Object.fromEntries(
    accounts.map((a) => [a.id, nameByUserId[a.customer_id] || '']),
  )
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_id: row.account_id,
    daily_limit_amount: Number(row.daily_limit_amount),
    last_reset_date: row.last_reset_date,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      // account_id can't change on an existing withdrawal limit, only the limit/reset date
      await api.put(`/withdrawal-limits/${editingId.value}`, {
        daily_limit_amount: form.value.daily_limit_amount,
        last_reset_date: form.value.last_reset_date,
      })
    } else {
      await api.post('/withdrawal-limits/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Withdrawal limit saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: err.response?.data?.detail || 'Save failed' })
  }
}

function removeRow (row) {
  Dialog.create({
    title: 'Confirm Delete',
    ok: { label: 'Delete', color: 'negative' },
    cancel: { label: 'Cancel', flat: true },
    message: `Delete withdrawal limit #${row.id}?`,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/withdrawal-limits/${row.id}`)
      $q.notify({ type: 'positive', message: 'Withdrawal limit deleted' })
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
