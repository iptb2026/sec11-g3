<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />

        <q-toolbar-title class="row items-center">
          <q-icon name="account_balance" class="q-mr-sm" size="24px" />
          <span class="text-weight-bold">Socnoben Mini Banking System</span>
        </q-toolbar-title>

        <q-space />

        <div class="row items-center q-gutter-sm">
          <q-chip
            square
            color="white"
            text-color="primary"
            class="text-weight-medium q-px-md"
            style="border-radius: 16px; background-color: rgba(255, 255, 255, 0.95);"
          >
            <q-avatar icon="account_circle" color="primary" text-color="white" size="24px" />
            <span class="q-ml-xs">{{ userDisplayBadge }}</span>
          </q-chip>

          <q-btn
            flat
            round
            dense
            icon="logout"
            aria-label="Logout"
            @click="onLogout"
            class="text-white"
          >
            <q-tooltip>Logout</q-tooltip>
          </q-btn>
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered class="bg-grey-1">
      <q-list padding class="text-grey-9">
        <q-item-label header class="text-weight-bold text-uppercase text-caption text-grey-7">NAVIGATION</q-item-label>
        <q-item clickable to="/" exact active-class="bg-blue-1 text-primary text-weight-bold">
          <q-item-section avatar>
            <q-icon name="dashboard" color="primary" />
          </q-item-section>
          <q-item-section>Dashboard</q-item-section>
        </q-item>

        <q-separator class="q-my-sm" />

        <q-item-label header class="text-weight-bold text-uppercase text-caption text-grey-7">SYSTEM CONFIGURATION</q-item-label>
        <q-item
          clickable
          to="/admin/roles"
          :disable="!auth.isAdmin"
          :class="!auth.isAdmin ? 'text-grey-5' : ''"
          active-class="bg-blue-1 text-primary text-weight-bold"
        >
          <q-item-section avatar>
            <q-icon name="admin_panel_settings" :color="auth.isAdmin ? 'primary' : 'grey-5'" />
          </q-item-section>
          <q-item-section>Roles</q-item-section>
        </q-item>

        <q-item
          clickable
          to="/admin/account-types"
          :disable="!auth.isAdmin"
          :class="!auth.isAdmin ? 'text-grey-5' : ''"
          active-class="bg-blue-1 text-primary text-weight-bold"
        >
          <q-item-section avatar>
            <q-icon name="credit_card" :color="auth.isAdmin ? 'primary' : 'grey-5'" />
          </q-item-section>
          <q-item-section>Account Types</q-item-section>
        </q-item>

        <q-item
          clickable
          to="/admin/banks"
          :disable="auth.isCustomer"
          :class="auth.isCustomer ? 'text-grey-5' : ''"
          active-class="bg-blue-1 text-primary text-weight-bold"
        >
          <q-item-section avatar>
            <q-icon name="account_balance" :color="!auth.isCustomer ? 'primary' : 'grey-5'" />
          </q-item-section>
          <q-item-section>Banks</q-item-section>
        </q-item>

        <q-item
          clickable
          to="/admin/fee-types"
          :disable="!auth.isAdmin"
          :class="!auth.isAdmin ? 'text-grey-5' : ''"
          active-class="bg-blue-1 text-primary text-weight-bold"
        >
          <q-item-section avatar>
            <q-icon name="sell" :color="auth.isAdmin ? 'primary' : 'grey-5'" />
          </q-item-section>
          <q-item-section>Fee Types</q-item-section>
        </q-item>

        <q-item
          clickable
          to="/admin/users"
          :disable="!auth.isAdmin"
          :class="!auth.isAdmin ? 'text-grey-5' : ''"
          active-class="bg-blue-1 text-primary text-weight-bold"
        >
          <q-item-section avatar>
            <q-icon name="people" :color="auth.isAdmin ? 'primary' : 'grey-5'" />
          </q-item-section>
          <q-item-section>Users</q-item-section>
        </q-item>

        <q-item
          clickable
          to="/admin/audit-logs"
          :disable="!auth.isAdmin"
          :class="!auth.isAdmin ? 'text-grey-5' : ''"
          active-class="bg-blue-1 text-primary text-weight-bold"
        >
          <q-item-section avatar>
            <q-icon name="history" :color="auth.isAdmin ? 'primary' : 'grey-5'" />
          </q-item-section>
          <q-item-section>Audit Logs</q-item-section>
        </q-item>

        <q-separator class="q-my-sm" />

        <q-item-label header class="text-weight-bold text-uppercase text-caption text-grey-7">BANKING OPERATIONS</q-item-label>
        <q-item
          clickable
          to="/accounts"
          active-class="bg-blue-1 text-primary text-weight-bold"
        >
          <q-item-section avatar>
            <q-icon name="account_box" color="primary" />
          </q-item-section>
          <q-item-section>Accounts</q-item-section>
        </q-item>

        <q-item
          clickable
          to="/withdrawal-limits"
          :disable="auth.isCustomer"
          :class="auth.isCustomer ? 'text-grey-5' : ''"
          active-class="bg-blue-1 text-primary text-weight-bold"
        >
          <q-item-section avatar>
            <q-icon name="speed" :color="!auth.isCustomer ? 'primary' : 'grey-5'" />
          </q-item-section>
          <q-item-section>Withdrawal Limits</q-item-section>
        </q-item>

        <q-item
          clickable
          to="/interest-policies"
          :disable="auth.isCustomer"
          :class="auth.isCustomer ? 'text-grey-5' : ''"
          active-class="bg-blue-1 text-primary text-weight-bold"
        >
          <q-item-section avatar>
            <q-icon name="timeline" :color="!auth.isCustomer ? 'primary' : 'grey-5'" />
          </q-item-section>
          <q-item-section>Interest Policies</q-item-section>
        </q-item>

        <q-item
          clickable
          to="/ledger-entries"
          active-class="bg-blue-1 text-primary text-weight-bold"
        >
          <q-item-section avatar>
            <q-icon name="bar_chart" color="primary" />
          </q-item-section>
          <q-item-section>Reports</q-item-section>
        </q-item>

        <template v-if="auth.isAdmin || auth.isStaff">
          <q-separator class="q-my-sm" />
          <q-item-label header class="text-weight-bold text-uppercase text-caption text-grey-7">TRANSACTIONS & LEDGER</q-item-label>
          <q-item clickable to="/deposits" active-class="bg-blue-1 text-primary text-weight-bold">
            <q-item-section avatar><q-icon name="add_card" color="primary" /></q-item-section>
            <q-item-section>Deposits</q-item-section>
          </q-item>
          <q-item clickable to="/withdrawals" active-class="bg-blue-1 text-primary text-weight-bold">
            <q-item-section avatar><q-icon name="remove_circle" color="primary" /></q-item-section>
            <q-item-section>Withdrawals</q-item-section>
          </q-item>
          <q-item clickable to="/transfers" active-class="bg-blue-1 text-primary text-weight-bold">
            <q-item-section avatar><q-icon name="swap_horiz" color="primary" /></q-item-section>
            <q-item-section>Transfers</q-item-section>
          </q-item>
          <q-item clickable to="/interbank-transfers" active-class="bg-blue-1 text-primary text-weight-bold">
            <q-item-section avatar><q-icon name="sync_alt" color="primary" /></q-item-section>
            <q-item-section>Interbank Transfers</q-item-section>
          </q-item>
          <q-item clickable to="/fee-records" active-class="bg-blue-1 text-primary text-weight-bold">
            <q-item-section avatar><q-icon name="receipt_long" color="primary" /></q-item-section>
            <q-item-section>Fee Records</q-item-section>
          </q-item>
          <q-item clickable to="/interest-records" active-class="bg-blue-1 text-primary text-weight-bold">
            <q-item-section avatar><q-icon name="savings" color="primary" /></q-item-section>
            <q-item-section>Interest Records</q-item-section>
          </q-item>
        </template>
      </q-list>
    </q-drawer>

    <q-page-container class="bg-grey-2">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, computed } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth-store"

const leftDrawerOpen = ref(true)
const auth = useAuthStore()
const router = useRouter()

const userDisplayBadge = computed(() => {
  if (auth.isAdmin) {
    return auth.fullName ? `${auth.fullName} (System Admin)` : "Administrator (System Admin)"
  }
  if (auth.isStaff) {
    return auth.fullName ? `${auth.fullName} (Bank Teller)` : "Staff Member (Bank Teller)"
  }
  if (auth.isCustomer) {
    return auth.fullName ? `${auth.fullName} (Client)` : "Customer User (Client)"
  }
  return auth.username || "User"
})

function onLogout () {
  auth.logout()
  router.push("/login")
}
</script>
