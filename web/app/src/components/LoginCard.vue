<script setup lang="ts">
import { useAuthStore } from 'stores/auth'

const emit = defineEmits<{
  loggedIn: [Record<string, any>]
  needsVerification: []
}>()

const $q = useQuasar()
const { login } = useAuthStore()

const showPasswordStatus = ref(false)
const loading = ref(false)

const state = reactive({
  email: null,
  password: null,
})

const errors = ref({
  email: null,
  password: null,
})

const handleLoginError = (error: any) => {
  console.error(error)
  const errorResponse: any = error.data || error.response?._data

  const alertState = {
    color: 'danger',
    title: 'Authentication Failed',
    description: 'Please check your credentials and try again.',
    icon: 'fa-solid fa-circle-exclamation',
  }

  if (errorResponse.status === 400) {
    const firstError = errorResponse.errors?.[0]
    if (firstError?.code === 'email_password_mismatch') {
      errors.value.email = ' '
      errors.value.password = firstError.message
      return
    } else if (firstError?.code === 'invalid') {
      errors.value[firstError.param] = firstError.message
      return
    } else if (firstError?.code === 'too_many_login_attempts') {
      alertState.color = 'warning'
      alertState.title = 'Too Many Login Attempts'
      alertState.description = 'Please try again later.'
      alertState.icon = 'fa-solid fa-circle-exclamation'
      return
    } else if (firstError?.code === 'account_disabled') {
      alertState.color = 'warning'
      alertState.title = 'Account Disabled'
      alertState.description = 'Your account has been disabled. Please contact support.'
      alertState.icon = 'fa-solid fa-circle-exclamation'
      return
    }
  }

  if (errorResponse.status === 401) {
    const flows = errorResponse.data?.flows || []

    // Check for verify_email flow
    const verifyEmailFlow = flows.find(flow => flow.id === 'verify_email')
    if (verifyEmailFlow?.is_pending) {
      alertState.color = 'warning'
      alertState.title = 'Email Verification Required'
      alertState.description = 'Please check your email and verify your account.'
      alertState.icon = 'fa-solid fa-envelope'
      emit('needsVerification')
    }
  } else {
    alertState.description = 'An unexpected error occurred. Please try again later.'
  }

  $q.notify({
    position: 'top-right',
    message: alertState.title,
    caption: alertState.description,
    color: alertState.color,
    icon: alertState.icon,
  })
}

const onLoginSubmit = async () => {
  try {
    loading.value = true
    const res = await login(state)
    emit('loggedIn', res)
  } catch (error: any) {
    handleLoginError(error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="row justify-center items-center bg-white q-pa-md">
    <div class="full-width q-px-md">
      <q-form autofocus class="text-sm" @submit="onLoginSubmit">
        <q-input
          v-model="state.email"
          input-class="text-body1"
          label="Email"
          :error="!!errors.email"
          :error-message="errors.email"
        >
          <template #before>
            <q-icon name="fa-solid fa-envelope" />
          </template>
        </q-input>
        <q-input
          v-model="state.password"
          input-class="text-body1"
          label="Password"
          :error="!!errors.password"
          :error-message="errors.password"
          :type="showPasswordStatus ? 'text' : 'password'"
        >
          <template #before>
            <q-icon name="fa-solid fa-lock" />
          </template>
          <template #append>
            <q-icon class="cursor-pointer" :name="showPasswordStatus ? 'mdi-eye' : 'mdi-eye-off'" @click="showPasswordStatus = !showPasswordStatus" />
          </template>
        </q-input>
        <div class="text-center q-mt-xl">
          <q-btn class="bg-blue full-width text-white q-px-lg" type="submit" :loading="loading">
            Login
          </q-btn>
        </div>
      </q-form>
    </div>
  </div>
</template>
