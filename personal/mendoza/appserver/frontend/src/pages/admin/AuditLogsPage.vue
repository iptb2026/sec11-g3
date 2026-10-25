<template>
  <q-page class="q-pa-md q-pa-sm-lg">
    <!-- Modern Hero Header -->
    <div class="page-hero-banner">
      <div class="row items-center no-wrap">
        <q-avatar size="48px" class="bg-lavender-gradient text-white shadow-md q-mr-md gt-xs">
          <q-icon name="history" size="24px" />
        </q-avatar>
        <div>
          <div class="row items-center">
            <span class="text-h5 text-weight-bolder" style="color: #FFFFFF;">System Audit Logs</span>
            <q-badge color="accent" text-color="primary" class="q-ml-sm text-weight-bold">
              {{ rows.length }} Events
            </q-badge>
          </div>
          <div class="text-caption" style="color: #777784;">Real-time security trail of administrative actions and user events.</div>
        </div>
      </div>

      <!-- Android S Search Pill -->
      <div class="row items-center q-gutter-sm">
        <q-input
          v-model="filter"
          dense
          outlined
          placeholder="Search audit trail..."
          class="android-search-pill"
          style="min-width: 240px;"
        >
          <template #prepend>
            <q-icon name="search" color="primary" />
          </template>
          <template v-if="filter" #append>
            <q-icon name="close" class="cursor-pointer" @click="filter = ''" />
          </template>
        </q-input>
        <q-btn flat round dense icon="refresh" color="primary" :loading="loading" @click="loadRows">
          <q-tooltip>Reload</q-tooltip>
        </q-btn>
      </div>
    </div>

    <!-- Modern Data Table -->
    <q-table
      :rows="rows"
      :columns="columns"
      row-key="id"
      :loading="loading"
      :filter="filter"
      flat
      bordered
      class="modern-data-table shadow-sm"
    >
      <template #body-cell-action_type="props">
        <q-td :props="props">
          <q-chip
            size="sm"
            :color="getActionColor(props.value)"
            text-color="white"
            class="text-weight-bold"
            style="border-radius: 8px;"
          >
            {{ props.value }}
          </q-chip>
        </q-td>
      </template>

      <template #body-cell-ip_address="props">
        <q-td :props="props">
          <span class="font-mono text-caption text-weight-medium text-primary" style="background: rgba(229, 197, 131, 0.1); border: 1px solid rgba(229, 197, 131, 0.22); padding: 2px 8px; border-radius: 6px;">
            {{ props.value || '127.0.0.1' }}
          </span>
        </q-td>
      </template>

      <template #body-cell-action_timestamp="props">
        <q-td :props="props">
          <span class="text-caption text-grey-7">{{ formatTimestamp(props.value) }}</span>
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left', sortable: true },
  { name: 'user_id', label: 'User ID', field: 'user_id', align: 'left', sortable: true },
  { name: 'action_type', label: 'Action', field: 'action_type', align: 'left', sortable: true },
  { name: 'entity_name', label: 'Entity', field: 'entity_name', align: 'left', sortable: true },
  { name: 'entity_id', label: 'Entity ID', field: 'entity_id', align: 'left' },
  { name: 'ip_address', label: 'IP Address', field: 'ip_address', align: 'left' },
  { name: 'action_timestamp', label: 'Timestamp', field: 'action_timestamp', align: 'left', sortable: true },
]

const rows = ref([])
const loading = ref(false)
const filter = ref('')

function getActionColor (action) {
  if (!action) return 'grey-7'
  const act = action.toUpperCase()
  if (act.includes('CREATE') || act.includes('INSERT') || act.includes('DEPOSIT')) return 'positive'
  if (act.includes('DELETE') || act.includes('REMOVE') || act.includes('FAIL')) return 'negative'
  if (act.includes('UPDATE') || act.includes('EDIT')) return 'warning'
  return 'primary'
}

function formatTimestamp (ts) {
  if (!ts) return '—'
  return new Date(ts).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/audit-logs/')
    rows.value = data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRows()
})
</script>
