<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const { resetPassword } = useAuth()

const state = reactive({
  password: '',
  confirmPassword: '',
})

const loading = ref(false)
const error = ref({
  password: null,
  confirmPassword: null,
})

const handleSubmit = async () => {
  error.value = { password: null, confirmPassword: null }

  if (!state.password) {
    error.value.password = 'Password is required'
    return
  }

  if (state.password !== state.confirmPassword) {
    error.value.confirmPassword = 'Passwords do not match'
    return
  }

  loading.value = true

  try {
    const token = route.params.token as string
    await resetPassword({
      key: token,
      password: state.password,
    })

    $q.notify({
      position: 'top-right',
      message: 'Password Reset Successfully',
      caption: 'You can now log in with your new password',
      color: 'positive',
      icon: 'fa-solid fa-check-circle',
    })

    router.push('/login')
  } catch (err: any) {
    $q.notify({
      position: 'top-right',
      message: 'Reset Failed',
      caption: err.message || 'Please try again',
      color: 'negative',
      icon: 'fa-solid fa-circle-exclamation',
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <q-card-section class="text-center">
    <div class="text-h6">
      Reset Password
    </div>
  </q-card-section>

  <q-card-section>
    <q-form @submit.prevent="handleSubmit">
      <q-input
        v-model="state.password"
        label="New Password"
        type="password"
        :error="!!error.password"
        :error-message="error.password"
      >
        <template #before>
          <q-icon name="fa-solid fa-lock" />
        </template>
      </q-input>

      <q-input
        v-model="state.confirmPassword"
        class="q-mt-md"
        label="Confirm Password"
        type="password"
        :error="!!error.confirmPassword"
        :error-message="error.confirmPassword"
      >
        <template #before>
          <q-icon name="fa-solid fa-lock" />
        </template>
      </q-input>

      <div class="row justify-end q-mt-lg">
        <q-btn
          color="primary"
          label="Reset Password"
          type="submit"
          :loading="loading"
        />
      </div>
    </q-form>
  </q-card-section>
</template>
