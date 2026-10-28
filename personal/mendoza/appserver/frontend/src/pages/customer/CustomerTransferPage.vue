<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient shadow-md q-mr-md gt-xs">
          <q-icon name="swap_horiz" size="24px" />
        </q-avatar>
        <div>
          <div class="text-h5 text-weight-bolder">Transfer to a MyBank customer</div>
          <div class="text-caption text-secondary">Move funds securely between eligible MyBank accounts.</div>
        </div>
      </div>
    </div>

    <q-card v-if="success" class="glass-card q-mx-auto" style="max-width: 680px;">
      <q-card-section class="column items-center text-center q-py-xl">
        <q-avatar size="64px" color="positive" text-color="white" icon="check" class="q-mb-md" />
        <div class="text-h5 text-weight-bolder">Transfer successful</div>
        <div class="text-caption text-secondary q-mt-xs">Your money was sent securely.</div>
        <div class="text-h3 text-weight-bolder text-positive q-mt-md">
          ₱{{ formatAmount(success.amount) }}
        </div>
      </q-card-section>

      <q-separator />

      <q-card-section class="q-gutter-md">
        <div class="row justify-between items-start">
          <span class="text-secondary">From</span>
          <span class="text-weight-bold text-right">{{ success.senderName }}<br>{{ success.sourceAccountNumber }}</span>
        </div>
        <q-separator />
        <div class="row justify-between items-start">
          <span class="text-secondary">To</span>
          <span class="text-weight-bold text-right">{{ success.recipientName }}<br>{{ success.recipientAccountNumber }}</span>
        </div>
        <q-separator />
        <div class="row justify-between">
          <span class="text-secondary">Description</span>
          <span class="text-weight-medium">{{ success.remarks || '—' }}</span>
        </div>
        <q-separator />
        <div class="row justify-between">
          <span class="text-secondary">Transfer fee</span>
          <span class="text-weight-medium">₱{{ formatAmount(success.fee_amount) }}</span>
        </div>
        <q-separator />
        <div class="row justify-between">
          <span class="text-secondary">Total deducted</span>
          <span class="text-weight-bold">₱{{ formatAmount(success.total_debit) }}</span>
        </div>
        <q-separator />
        <div class="row justify-between">
          <span class="text-secondary">Date and time</span>
          <span class="text-weight-medium text-right">{{ formatDateTime(success.completed_at || success.created_at) }}</span>
        </div>
        <q-separator />
        <div class="row justify-between items-start">
          <span class="text-secondary">Reference number</span>
          <span class="text-weight-bold text-right" style="font-family: monospace;">{{ success.transfer_reference }}</span>
        </div>
        <q-banner dense rounded class="bg-grey-1 text-secondary">
          This receipt confirms the transfer was recorded. You can also find it in Transaction Activity.
        </q-banner>
      </q-card-section>

      <q-separator />

      <q-card-actions align="right" class="q-pa-md">
        <q-btn flat color="primary" icon="receipt_long" label="View activity" to="/my-transactions" />
        <q-btn flat color="primary" label="New transfer" @click="startAnotherTransfer" />
        <q-btn unelevated color="primary" icon="home" label="Back to dashboard" to="/" />
      </q-card-actions>
    </q-card>

    <q-card v-else class="glass-card q-mx-auto" style="max-width: 680px;">
      <q-card-section>
        <div class="text-h6 text-weight-bold">New transfer</div>
        <div class="text-caption text-secondary">Select one of your active accounts and verify the recipient before confirming.</div>
      </q-card-section>

      <q-separator />

      <q-card-section>
        <div v-if="loadingAccounts" class="text-center q-pa-lg">
          <q-spinner-dots color="primary" size="40px" />
          <div class="text-caption text-secondary q-mt-sm">Loading your eligible accounts...</div>
        </div>

        <q-banner v-else-if="accountLoadError" rounded class="bg-red-1 text-negative">
          Your accounts could not be loaded: {{ accountLoadError }}
        </q-banner>

        <q-banner v-else-if="accounts.length === 0" rounded class="bg-amber-1 text-dark">
          <template v-if="inactiveAccountCount > 0">
            We found {{ inactiveAccountCount }} account(s), but none are active for transfers. Please contact your bank for assistance.
          </template>
          <template v-else>
            No accounts are linked to your customer profile yet. Please contact your bank for assistance.
          </template>
        </q-banner>

        <q-form v-else ref="formRef" class="q-gutter-md" @submit.prevent="prepareTransfer">
          <q-select
            v-model="form.source_account_id"
            :options="accountOptions"
            label="Transfer from"
            outlined
            emit-value
            map-options
            :rules="[value => value !== null || 'Select a source account']"
            @update:model-value="clearRecipientPreview"
          >
            <template #option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label class="text-weight-bold">{{ scope.opt.label }}</q-item-label>
                  <q-item-label caption>{{ scope.opt.description }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>

          <div>
            <q-input
              v-model="form.destination_account_number"
              label="Recipient account number"
              outlined
              autocomplete="off"
              :rules="[value => !!value?.trim() || 'Enter the recipient account number']"
              @update:model-value="clearRecipientPreview"
            />
            <q-btn
              flat
              dense
              color="primary"
              icon="verified_user"
              label="Verify recipient"
              :loading="checkingRecipient"
              :disable="!form.source_account_id || !form.destination_account_number?.trim()"
              @click="lookupRecipient"
            />
            <div v-if="recipientError" class="text-negative text-caption q-mt-xs">{{ recipientError }}</div>
            <q-banner v-if="recipientPreview" rounded class="bg-green-1 text-positive q-mt-sm">
              <template #avatar>
                <q-icon name="person" color="positive" />
              </template>
              <div class="text-weight-bold">{{ recipientPreview.customer_name }}</div>
              <div class="text-caption">
                {{ recipientPreview.account_number }} · {{ recipientPreview.currency_code }} account
              </div>
            </q-banner>
          </div>

          <q-input
            v-model="form.amount"
            label="Amount"
            type="number"
            min="0.01"
            step="0.01"
            prefix="₱"
            outlined
            :rules="[
              value => Number(value) > 0 || 'Enter an amount greater than zero',
              value => /^\d+(\.\d{1,2})?$/.test(String(value)) || 'Enter no more than two decimal places',
              value => Number(value) + Number(recipientPreview?.transfer_fee || 0) <= Number(selectedAccount?.available_balance) || 'Amount and transfer fee exceed the available balance',
            ]"
          />

          <q-input
            v-model="form.remarks"
            label="Description (optional)"
            type="textarea"
            outlined
            autogrow
            maxlength="500"
          />

          <div class="row items-center justify-end q-gutter-sm">
            <q-btn flat color="primary" label="Cancel" to="/" />
            <q-btn
              unelevated
              color="primary"
              icon="arrow_forward"
              label="Review transfer"
              type="submit"
              :loading="checkingRecipient"
              :disable="submitting || checkingRecipient"
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>

    <q-dialog v-model="reviewDialog" persistent>
      <q-card class="glass-card" style="width: 500px; max-width: 95vw;">
        <q-card-section class="row items-center bg-lavender-soft-gradient">
          <q-avatar size="38px" color="primary" text-color="white" icon="swap_horiz" class="q-mr-sm" />
          <div>
            <div class="text-h6 text-weight-bold">Confirm transfer</div>
            <div class="text-caption text-secondary">Review the details before sending.</div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-sm">
          <div class="row justify-between">
            <span class="text-secondary">From</span>
            <span class="text-weight-bold">{{ selectedAccount?.account_number }}</span>
          </div>
          <div class="row justify-between">
            <span class="text-secondary">To</span>
            <span class="text-weight-bold text-right">{{ recipientPreview?.customer_name }} · {{ recipientPreview?.account_number }}</span>
          </div>
          <div class="row justify-between">
            <span class="text-secondary">Amount</span>
            <span class="text-weight-bold">₱{{ formatAmount(form.amount) }}</span>
          </div>
          <div class="row justify-between">
            <span class="text-secondary">Transfer fee</span>
            <span class="text-weight-medium">₱{{ formatAmount(recipientPreview?.transfer_fee) }}</span>
          </div>
          <div class="row justify-between">
            <span class="text-secondary">Total deducted</span>
            <span class="text-weight-bold">₱{{ formatAmount(Number(form.amount || 0) + Number(recipientPreview?.transfer_fee || 0)) }}</span>
          </div>
          <div v-if="form.remarks?.trim()" class="row justify-between">
            <span class="text-secondary">Description</span>
            <span class="text-weight-medium">{{ form.remarks.trim() }}</span>
          </div>
          <q-banner dense rounded class="bg-grey-1 text-secondary">
            The configured fee is deducted from your source account and recorded in your transaction history.
          </q-banner>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat color="grey-8" label="Cancel" :disable="submitting" @click="reviewDialog = false" />
          <q-btn unelevated color="primary" label="Confirm transfer" :loading="submitting" @click="submitTransfer" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

const $q = useQuasar()
const auth = useAuthStore()
const formRef = ref(null)
const loadingAccounts = ref(true)
const checkingRecipient = ref(false)
const submitting = ref(false)
const reviewDialog = ref(false)
const accounts = ref([])
const inactiveAccountCount = ref(0)
const accountLoadError = ref('')
const recipientPreview = ref(null)
const recipientError = ref('')
const success = ref(null)
const idempotencyKey = ref('')
const idempotencyPayload = ref('')
const form = ref({
  source_account_id: null,
  destination_account_number: '',
  amount: '',
  remarks: '',
})

const accountOptions = computed(() => accounts.value.map((account) => ({
  label: account.account_number,
  value: account.id,
  description: `${account.currency_code} · Available ₱${formatAmount(account.available_balance)}`,
})))

const selectedAccount = computed(() =>
  accounts.value.find((account) => account.id === form.value.source_account_id) || null,
)

function formatAmount (value) {
  const amount = Number(value)
  return Number.isFinite(amount)
    ? amount.toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    : '0.00'
}

function formatDateTime (value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString('en-PH')
}

function errorMessage (error) {
  const detail = error.response?.data?.detail
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || String(item)).join('; ')
  }
  return detail || error.message || 'The request could not be completed.'
}

function clearRecipientPreview () {
  recipientPreview.value = null
  recipientError.value = ''
}

watch(
  () => [form.value.source_account_id, form.value.destination_account_number],
  clearRecipientPreview,
)

async function loadAccounts () {
  const { data } = await api.get('/accounts/')
  if (!Array.isArray(data)) {
    throw new Error('The accounts service returned an unexpected response.')
  }
  const ownAccounts = data.filter((account) => String(account.customer_id) === String(auth.userId))
  accounts.value = ownAccounts.filter((account) => account.status === 'ACTIVE')
  inactiveAccountCount.value = ownAccounts.length - accounts.value.length
  accountLoadError.value = ''
  if (!accounts.value.some((account) => account.id === form.value.source_account_id)) {
    form.value.source_account_id = accounts.value[0]?.id ?? null
  }
}

async function lookupRecipient () {
  clearRecipientPreview()
  if (!form.value.source_account_id || !form.value.destination_account_number?.trim()) return false

  checkingRecipient.value = true
  try {
    const { data } = await api.post('/transfers/recipient-preview', {
      source_account_id: form.value.source_account_id,
      destination_account_number: form.value.destination_account_number.trim(),
    })
    recipientPreview.value = data
    return true
  } catch (error) {
    recipientError.value = errorMessage(error)
    return false
  } finally {
    checkingRecipient.value = false
  }
}

function newIdempotencyKey () {
  if (!window.crypto?.getRandomValues) {
    throw new Error('Secure transfer request identifiers are unavailable in this browser.')
  }
  const bytes = new Uint8Array(16)
  window.crypto.getRandomValues(bytes)
  bytes[6] = (bytes[6] & 0x0f) | 0x40
  bytes[8] = (bytes[8] & 0x3f) | 0x80
  const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('')
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`
}

async function prepareTransfer () {
  if (!await formRef.value.validate()) return
  if (!recipientPreview.value || recipientPreview.value.account_number !== form.value.destination_account_number.trim()) {
    if (!await lookupRecipient()) return
  }
  if (!await formRef.value.validate()) return

  const payload = {
    source_account_id: form.value.source_account_id,
    destination_account_number: form.value.destination_account_number.trim(),
    amount: String(form.value.amount),
    remarks: form.value.remarks.trim() || null,
  }
  const signature = JSON.stringify(payload)
  if (!idempotencyKey.value || idempotencyPayload.value !== signature) {
    try {
      idempotencyKey.value = newIdempotencyKey()
      idempotencyPayload.value = signature
    } catch (error) {
      $q.notify({ type: 'negative', message: error.message })
      return
    }
  }
  reviewDialog.value = true
}

async function submitTransfer () {
  if (submitting.value || !idempotencyKey.value) return
  submitting.value = true
  try {
    const payload = {
      source_account_id: form.value.source_account_id,
      destination_account_number: form.value.destination_account_number.trim(),
      amount: String(form.value.amount),
      remarks: form.value.remarks.trim() || null,
    }
    const { data } = await api.post('/transfers/', payload, {
      headers: { 'Idempotency-Key': idempotencyKey.value },
    })
    success.value = {
      ...data,
      senderName: auth.fullName || auth.username,
      sourceAccountNumber: selectedAccount.value?.account_number || String(data.source_account_id),
      recipientName: recipientPreview.value?.customer_name || recipientPreview.value?.account_number,
      recipientAccountNumber: recipientPreview.value?.account_number || form.value.destination_account_number.trim(),
      fee_amount: data.fee_amount ?? recipientPreview.value?.transfer_fee ?? '0.00',
      total_debit: data.total_debit ?? (
        Number(data.amount) + Number(recipientPreview.value?.transfer_fee || 0)
      ),
    }
    reviewDialog.value = false
    $q.notify({ type: 'positive', message: 'Transfer completed successfully' })

    form.value.destination_account_number = ''
    form.value.amount = ''
    form.value.remarks = ''
    idempotencyKey.value = ''
    idempotencyPayload.value = ''
    recipientPreview.value = null

    try {
      await loadAccounts()
    } catch (error) {
      $q.notify({ type: 'warning', message: `Transfer succeeded, but account balances could not be refreshed: ${errorMessage(error)}` })
    }
  } catch (error) {
    $q.notify({ type: 'negative', message: errorMessage(error) })
  } finally {
    submitting.value = false
  }
}

function startAnotherTransfer () {
  success.value = null
  clearRecipientPreview()
  form.value.amount = ''
  form.value.destination_account_number = ''
  form.value.remarks = ''
  idempotencyKey.value = ''
  idempotencyPayload.value = ''
}

onMounted(async () => {
  try {
    await loadAccounts()
  } catch (error) {
    accountLoadError.value = errorMessage(error)
    $q.notify({ type: 'negative', message: `Could not load your accounts: ${accountLoadError.value}` })
  } finally {
    loadingAccounts.value = false
  }
})
</script>
