<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page class="flex flex-center bg-login-gradient q-pa-md" style="min-height: 100vh;">
        <div style="width: 100%; max-width: 420px;">
          <!-- Top Brand Emblem -->
          <div class="text-center q-mb-md">
            <div class="row justify-center q-mb-sm">
              <BrandLogo :size="64" theme="dark" />
            </div>
            <div class="text-h4 text-weight-bolder text-white" style="letter-spacing: -0.02em;">MyBank</div>
            <div class="text-caption text-weight-medium text-secondary">Secure Digital Banking Portal</div>
          </div>

          <!-- Glassmorphism Login Card -->
          <q-card class="glass-card q-pa-lg">
            <q-card-section class="q-pt-xs q-pb-md text-center">
              <div class="text-h6 text-weight-bold text-white">Welcome Back</div>
              <div class="text-caption text-secondary">Please sign in with your credentials</div>
            </q-card-section>

            <q-card-section class="q-pa-none">
              <q-form @submit="onSubmit" class="column q-gutter-md">
                <q-input
                  v-model="username"
                  label="Username"
                  outlined
                  autofocus
                  :rules="[(val) => !!val || 'Username is required']"
                >
                  <template #prepend>
                    <q-icon name="person" color="primary" />
                  </template>
                </q-input>

                <q-input
                  v-model="password"
                  label="Password"
                  outlined
                  :type="showPassword ? 'text' : 'password'"
                  :rules="[(val) => !!val || 'Password is required']"
                >
                  <template #prepend>
                    <q-icon name="lock" color="primary" />
                  </template>
                  <template #append>
                    <q-icon
                      :name="showPassword ? 'visibility_off' : 'visibility'"
                      class="cursor-pointer"
                      @click="showPassword = !showPassword"
                    />
                  </template>
                </q-input>

                <!-- Error Alert -->
                <q-banner v-if="errorMessage" dense class="bg-red-1 text-red-9 rounded-borders q-pa-sm">
                  <template #avatar>
                    <q-icon name="error_outline" color="negative" size="22px" />
                  </template>
                  <span class="text-caption text-weight-medium">{{ errorMessage }}</span>
                </q-banner>

                <q-btn
                  type="submit"
                  label="Sign In"
                  icon-right="arrow_forward"
                  color="primary"
                  class="full-width q-py-sm text-weight-bold"
                  size="md"
                  :loading="loading"
                  unelevated
                  style="border-radius: 14px;"
                />
              </q-form>
            </q-card-section>
          </q-card>

          <!-- Security Badge Footer -->
          <div class="row items-center justify-center q-mt-lg text-caption text-secondary">
            <q-icon name="verified_user" size="16px" color="positive" class="q-mr-xs" />
            <span>256-bit SSL Encrypted • Multi-Tier Security</span>
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth-store'
import BrandLogo from '@/components/BrandLogo.vue'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

const auth = useAuthStore()
const router = useRouter()

async function onSubmit () {
  loading.value = true
  errorMessage.value = ''
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    if (err.response) {
      // Backend rejected the request (e.g. wrong credentials on /auth/login)
      errorMessage.value = err.response.data?.detail || `Login failed (HTTP ${err.response.status}).`
    } else if (err.request) {
      // Request never got a response at all: wrong API base URL, backend down, or CORS block
      errorMessage.value = 'Could not reach the backend API. Check that it is running and that the API base URL in .env is correct.'
    } else {
      // Something failed in our own post-login logic (e.g. no matching user record)
      errorMessage.value = err.message || 'Login failed for an unknown reason.'
    }
  } finally {
    loading.value = false
  }
}
</script>
