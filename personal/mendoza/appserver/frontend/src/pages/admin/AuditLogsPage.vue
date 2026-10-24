<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Audit Logs</div>
      <q-space />
    </div>

    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered>
    </q-table>

  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'user_id', label: 'User ID', field: 'user_id', align: 'left' },
  { name: 'action_type', label: 'Action', field: 'action_type', align: 'left' },
  { name: 'entity_name', label: 'Entity', field: 'entity_name', align: 'left' },
  { name: 'entity_id', label: 'Entity ID', field: 'entity_id', align: 'left' },
  { name: 'ip_address', label: 'IP Address', field: 'ip_address', align: 'left' },
  { name: 'action_timestamp', label: 'Timestamp', field: 'action_timestamp', align: 'left' },
]

const rows = ref([])
const loading = ref(false)

async function loadRows () {
  loading.value = true
  const { data } = await api.get('/audit-logs/')
  rows.value = data
  loading.value = false
}

onMounted(() => {
  loadRows()
})
</script>
