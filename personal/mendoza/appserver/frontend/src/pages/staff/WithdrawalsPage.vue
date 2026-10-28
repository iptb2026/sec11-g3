<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Page Hero Banner -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="remove_circle" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">Withdrawals</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Records
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Process and monitor account debit and withdrawal transactions.</div>
        </div>
      </div>

      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Filter withdrawals..."
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
          label="New Withdrawal"
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
      <template #body-cell-reference_number="props">
        <q-td :props="props">
          <span class="text-caption text-weight-medium" style="font-family: monospace; color: #FFFFFF;">
            {{ props.value || '—' }}
          </span>
        </q-td>
      </template>

      <template #body-cell-amount="props">
        <q-td :props="props" class="text-negative text-weight-bolder">
          -₱{{ Number(props.value).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </q-td>
      </template>

      <template #body-cell-withdrawal_channel="props">
        <q-td :props="props">
          <q-chip
            dense
            color="red-1"
            text-color="negative"
            class="text-weight-bold"
            style="font-size: 0.72rem;"
          >
            {{ props.value }}
          </q-chip>
        </q-td>
      </template>
    </q-table>

    <!-- Create Dialog -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 440px; max-width: 95vw;" class="glass-card">
        <q-card-section class="row items-center bg-lavender-soft-gradient q-py-md">
          <q-avatar size="36px" color="primary" text-color="white" icon="remove_circle" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold" style="color: #FFFFFF;">New Withdrawal</div>
            <div class="text-caption text-grey-7">Record a debit transaction from a customer account</div>
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

          <q-input v-model.number="form.amount" label="Amount (PHP)" type="number" outlined />
          <q-select
            v-model="form.withdrawal_channel"
            label="Channel"
            outlined
            emit-value
            map-options
            use-input
            hide-selected
            fill-input
            input-debounce="0"
            new-value-mode="add-unique"
            :options="filteredChannelOptions"
            @filter="filterChannelOptions"
            hint="Use an existing valid channel for the account and transaction"
          />
          <q-input v-model="form.remarks" label="Remarks" type="textarea" outlined rows="2" />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md bg-grey-1">
          <q-btn flat label="Cancel" color="grey-8" v-close-popup />
          <q-btn unelevated color="primary" label="Save Withdrawal" class="text-weight-bold" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_number', label: 'Account Number', field: (row) => accountNumberByAccountId.value[row.account_id] || '', align: 'left' },
  { name: 'account_name', label: 'Account Name', field: (row) => accountHolderByAccountId.value[row.account_id] || '', align: 'left' },
  { name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'withdrawal_channel', label: 'Channel', field: 'withdrawal_channel', align: 'left' },
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left' },
]

const rows = ref([])
const filter = ref('')
const accountOptions = ref([])
const accountNumberByAccountId = ref({})
const accountHolderByAccountId = ref({})
const userNameByUserId = ref({})
const loading = ref(false)
const showDialog = ref(false)
const emptyForm = () => ({ account_id: null, amount: 0, withdrawal_channel: 'BRANCH', remarks: '' })
const form = ref(emptyForm())

const accountHolderName = computed(() => accountHolderByAccountId.value[form.value.account_id] || '')

const channelOptions = [
  { label: 'ONLINE', value: 'ONLINE' },
  { label: 'ATM', value: 'ATM' },
  { label: 'Teller (Branch)', value: 'BRANCH' },
]
const filteredChannelOptions = ref(channelOptions)
function filterChannelOptions (val, update) {
  update(() => {
    if (val === '') {
      filteredChannelOptions.value = channelOptions
    } else {
      const needle = val.toLowerCase()
      filteredChannelOptions.value = channelOptions.filter((v) => v.label.toLowerCase().includes(needle))
    }
  })
}

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/withdrawals/')
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
    nameByUserId[u.id] = `${u.first_name} ${u.last_name}`.trim()
  })
  userNameByUserId.value = nameByUserId

  accountOptions.value = accounts.map((a) => ({
    label: a.account_number,
    value: a.id,
    holder: nameByUserId[a.customer_id] || '',
  }))
  accountNumberByAccountId.value = Object.fromEntries(accounts.map((a) => [a.id, a.account_number]))
  accountHolderByAccountId.value = Object.fromEntries(
    accounts.map((a) => [a.id, nameByUserId[a.customer_id] || '']),
  )
}

function openCreate () {
  form.value = emptyForm()
  showDialog.value = true
}

async function save () {
  try {
    await api.post('/withdrawals/', form.value)
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Withdrawal recorded' })
    await loadRows()
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.detail || 'Failed to record withdrawal'
    })
  }
}

onMounted(() => {
  loadRows()
  loadOptions()
})
</script>
