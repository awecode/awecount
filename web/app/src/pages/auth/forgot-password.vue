<script setup lang="ts">
import AuthLayout from 'layouts/AuthLayout.vue'
import { useAuthStore } from 'stores/auth'

const { requestPasswordReset } = useAuthStore()
const $q = useQuasar()

const email = ref('')
const loading = ref(false)
const error = ref(null)

const router = useRouter()

const handleSubmit = async () => {
  if (!email.value) return

  loading.value = true
  error.value = null

  try {
    await requestPasswordReset(email.value)

    $q.notify({
      position: 'top-right',
      message: 'Reset Link Sent',
      caption: 'Please check your email',
      color: 'positive',
      icon: 'fa-solid fa-envelope',
    })

    router.push('/login')
  } catch (err: any) {
    error.value = err.message || 'Failed to send reset link'

    $q.notify({
      position: 'top-right',
      message: 'Request Failed',
      caption: error.value,
      color: 'negative',
      icon: 'fa-solid fa-circle-exclamation',
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout>
    <q-card-section class="text-center">
      <div class="text-h6">
        Forgot Password
      </div>
      <div class="text-caption text-grey-7 q-mt-sm">
        Enter your email address and we'll send you a link to reset your password.
      </div>
    </q-card-section>

    <q-card-section>
      <q-form @submit.prevent="handleSubmit">
        <q-input
          v-model="email"
          label="Email"
          type="email"
          :error="!!error"
          :error-message="error"
        >
          <template #before>
            <q-icon name="fa-solid fa-envelope" />
          </template>
        </q-input>

        <div class="row justify-between q-mt-lg">
          <q-btn
            flat
            color="primary"
            label="Back to Login"
            to="/login"
          />
          <q-btn
            color="primary"
            label="Send Reset Link"
            type="submit"
            :loading="loading"
          />
        </div>
      </q-form>
    </q-card-section>
  </AuthLayout>
</template>
