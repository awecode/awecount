<script setup lang="ts">
import AuthLayout from 'layouts/AuthLayout.vue'
import { useAuthStore } from 'stores/auth'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const { verifyEmail } = useAuthStore()

const loading = ref(true)
const error = ref(null)

const handleSuccess = () => {
  $q.notify({
    position: 'top-right',
    message: 'Email Verified Successfully',
    caption: 'You can now log in',
    color: 'positive',
    icon: 'fa-solid fa-check-circle',
  })

  router.push('/login')
}

onMounted(async () => {
  try {
    const token = route.params.token as string
    await verifyEmail(token)
    handleSuccess()
  } catch (err: any) {
    if (err.data?.status === 401 && err.data?.meta?.is_authenticated === false) {
      handleSuccess()
      return
    } else if (err.data?.status === 400 && err.data?.errors?.find((e: any) => e.code === 'invalid_or_expired_key')) {
      error.value = 'Verification link has expired'
      return
    }

    error.value = err.message || 'Verification failed'

    $q.notify({
      position: 'top-right',
      message: 'Verification Failed',
      caption: error.value,
      color: 'negative',
      icon: 'fa-solid fa-circle-exclamation',
    })
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AuthLayout>
    <div class="text-center q-py-lg">
      <div v-if="loading">
        <q-spinner color="primary" size="3em" />
        <div class="text-h6 q-mt-md">
          Verifying your email...
        </div>
      </div>

      <div v-else-if="error">
        <q-icon color="negative" name="error" size="3em" />
        <div class="text-h6 text-negative q-mt-md">
          {{ error }}
        </div>
        <q-btn
          flat
          class="q-mt-md"
          color="primary"
          label="Back to Login"
          to="/login"
        />
      </div>
    </div>
  </AuthLayout>
</template>
