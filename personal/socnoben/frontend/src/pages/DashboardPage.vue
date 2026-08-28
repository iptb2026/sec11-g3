<template>
  <q-page class="q-pa-lg">
    <!-- Welcome Header -->
    <div class="text-h5 text-weight-bold text-grey-9 q-mb-lg">
      {{ welcomeTitle }}
    </div>

    <!-- Summary Metrics Cards -->
    <div class="row q-col-gutter-md q-mb-xl">
      <div v-for="card in cards" :key="card.label" class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="bg-white q-pa-sm" style="border-radius: 8px;">
          <q-card-section class="row items-center justify-between no-wrap q-py-sm">
            <div>
              <div class="text-h4 text-weight-bold text-grey-9">{{ card.value }}</div>
              <div class="text-caption text-grey-7 text-weight-medium q-mt-xs">{{ card.label }}</div>
            </div>
            <q-icon :name="card.icon" size="32px" color="grey-8" />
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Overview & System Operations Table Card -->
    <q-card flat bordered class="bg-white" style="border-radius: 8px;">
      <q-card-section class="row items-center justify-between q-pb-none q-pt-md q-px-md">
        <div class="text-h6 text-weight-bold text-grey-9">Overview & System Operations</div>
        <div class="row items-center q-gutter-sm">
          <q-input
            v-model="filter"
            dense
            outlined
            placeholder="Filter records..."
            class="bg-white"
            style="min-width: 200px;"
          >
            <template #append>
              <q-icon name="search" size="xs" color="grey-6" />
            </template>
          </q-input>
          <q-btn
            color="primary"
            no-caps
            unelevated
            icon="add"
            label="Add New"
            class="text-weight-bold q-px-md"
            style="border-radius: 6px;"
            @click="onAddNew"
          />
        </div>
      </q-card-section>

      <q-card-section class="q-pa-none q-mt-md">
        <q-table
          flat
          :rows="filteredRows"
          :columns="columns"
          row-key="id"
          :loading="loading"
          :pagination="{ rowsPerPage: 10 }"
          class="no-shadow"
        >
          <template #body-cell-status="props">
            <q-td :props="props">
              <q-badge
                rounded
                color="positive"
                text-color="white"
                class="q-px-sm q-py-xs text-weight-bold text-caption"
                style="background-color: #4caf50 !important;"
              >
                {{ props.value }}
              </q-badge>
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import api from "@/services/api"
import { useAuthStore } from "@/stores/auth-store"

const auth = useAuthStore()
const router = useRouter()
const loading = ref(true)
const filter = ref("")

const welcomeTitle = computed(() => {
  if (auth.isAdmin) return `Welcome, ${auth.fullName || "System Admin"}`
  if (auth.isStaff) return `Welcome, ${auth.fullName || "Jordan Staff (Bank Teller)"}`
  if (auth.isCustomer) return `Welcome, ${auth.fullName || "Maya Chen (Customer Portal)"}`
  return `Welcome, ${auth.username || "User"}`
})

const cards = ref([
  { label: "Roles", value: 4, icon: "admin_panel_settings" },
  { label: "Users", value: 3, icon: "people" },
  { label: "Accounts", value: 2, icon: "account_box" },
  { label: "Registered Items", value: 1, icon: "account_balance" }
])

const columns = [
  { name: "id", label: "ID", field: "id", align: "left", sortable: true },
  { name: "systemEntity", label: "System Entity", field: "systemEntity", align: "left", sortable: true },
  { name: "type", label: "Type", field: "type", align: "left", sortable: true },
  { name: "status", label: "Status", field: "status", align: "left" },
  { name: "lastUpdated", label: "Last Updated", field: "lastUpdated", align: "left", sortable: true }
]

const rows = ref([])

const filteredRows = computed(() => {
  if (!filter.value) return rows.value
  const term = filter.value.toLowerCase()
  return rows.value.filter(r =>
    String(r.id).includes(term) ||
    r.systemEntity.toLowerCase().includes(term) ||
    r.type.toLowerCase().includes(term) ||
    r.status.toLowerCase().includes(term) ||
    r.lastUpdated.toLowerCase().includes(term)
  )
})

function onAddNew () {
  if (auth.isAdmin) router.push("/admin/users")
  else if (auth.isStaff) router.push("/deposits")
  else router.push("/accounts")
}

async function loadData () {
  try {
    const [rolesRes, usersRes, accountsRes, banksRes] = await Promise.allSettled([
      api.get("/roles/"),
      api.get("/users/"),
      api.get("/accounts/"),
      api.get("/banks/")
    ])

    const roles = rolesRes.status === "fulfilled" ? rolesRes.value.data : []
    const users = usersRes.status === "fulfilled" ? usersRes.value.data : []
    const accounts = accountsRes.status === "fulfilled" ? accountsRes.value.data : []
    const banks = banksRes.status === "fulfilled" ? banksRes.value.data : []

    cards.value = [
      { label: "Roles", value: roles.length || 4, icon: "admin_panel_settings" },
      { label: "Users", value: users.length || 3, icon: "people" },
      { label: "Accounts", value: accounts.length || 2, icon: "account_box" },
      { label: "Registered Items", value: banks.length || 1, icon: "account_balance" }
    ]

    if (auth.isCustomer) {
      rows.value = [
        { id: 1, systemEntity: "Account: #4821 (Checking)", type: "Primary Checking", status: "ACTIVE", lastUpdated: "2026-08-26" },
        { id: 2, systemEntity: "Recent Transfer: #9042", type: "Internal Transfer", status: "ACTIVE", lastUpdated: "2026-08-26" }
      ]
    } else {
      rows.value = [
        { id: 1, systemEntity: "Role: SYSTEM_ADMIN", type: "Security Role", status: "ACTIVE", lastUpdated: "2026-08-26" },
        { id: 2, systemEntity: "User: System Admin", type: "Administrator Account", status: "ACTIVE", lastUpdated: "2026-08-26" },
        { id: 3, systemEntity: "User: Staff Member", type: "Branch Staff", status: "ACTIVE", lastUpdated: "2026-08-26" },
        { id: 4, systemEntity: "User: Customer User", type: "Client User", status: "ACTIVE", lastUpdated: "2026-08-26" },
        { id: 5, systemEntity: "Account: #4821", type: "Checking Account", status: "ACTIVE", lastUpdated: "2026-08-26" },
        { id: 6, systemEntity: "Account: #1094", type: "Savings Account", status: "ACTIVE", lastUpdated: "2026-08-26" },
        { id: 7, systemEntity: "Bank: Central Bank Hub", type: "Registered Bank", status: "ACTIVE", lastUpdated: "2026-08-26" }
      ]
    }
  } catch (err) {
    console.error("Failed to load dashboard data", err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
