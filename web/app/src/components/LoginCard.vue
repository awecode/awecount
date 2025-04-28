<script setup lang="ts">
import { useAuthStore } from 'stores/auth'

const emit = defineEmits<{
  loggedIn: [Record<string, any>]
}>()

const $q = useQuasar()
const { login, requestEmailVerification } = useAuthStore()

const showPasswordStatus = ref(false)
const loading = ref(false)
const showVerificationModal = ref(false)
const resendCooldown = ref(0)

const state = reactive({
  email: null,
  password: null,
})

const errors = ref({
  email: null,
  password: null,
})

const startResendCooldown = () => {
  resendCooldown.value = 180
  const timer = setInterval(() => {
    if (resendCooldown.value > 0) {
      resendCooldown.value--
    } else {
      clearInterval(timer)
    }
  }, 1000)
}

const handleLoginError = (error: any) => {
  const errorResponse: any = error.data || error.response?._data

  if (errorResponse.status === 401) {
    const flows = errorResponse.data?.flows || []
    const verifyEmailFlow = flows.find((flow: any) => flow.id === 'verify_email')

    if (verifyEmailFlow && verifyEmailFlow.is_pending) {
      showVerificationModal.value = true
      startResendCooldown()
      return
    }
  }

  if (errorResponse.status === 409) {
    $q.notify({
      position: 'top-right',
      message: 'You are already logged in',
      caption: 'Please log out to continue',
      color: 'warning',
      icon: 'fa-solid fa-circle-exclamation',
    })
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
      $q.notify({
        position: 'top-right',
        message: 'Too Many Login Attempts',
        caption: 'Please try again later.',
        color: 'warning',
        icon: 'fa-solid fa-circle-exclamation',
      })
      return
    } else if (firstError?.code === 'account_disabled') {
      $q.notify({
        position: 'top-right',
        message: 'Account Disabled',
        caption: 'Your account has been disabled. Please contact support.',
        color: 'warning',
        icon: 'fa-solid fa-circle-exclamation',
      })
      return
    }
  }

  $q.notify({
    position: 'top-right',
    message: 'Login Failed',
    caption: error.message || 'Please try again later',
    color: 'negative',
    icon: 'fa-solid fa-circle-exclamation',
  })

  console.error(error)
}

const handleResendVerification = async () => {
  try {
    if (!state.email || resendCooldown.value > 0) return
    await requestEmailVerification(state.email)
    startResendCooldown()
    $q.notify({
      position: 'top-right',
      message: 'Verification Email Sent',
      caption: 'Please check your inbox',
      color: 'positive',
      icon: 'fa-solid fa-envelope',
    })
  } catch (error: any) {
    $q.notify({
      position: 'top-right',
      message: 'Failed to Resend',
      caption: error.message || 'Please try again later',
      color: 'negative',
      icon: 'fa-solid fa-circle-exclamation',
    })
  }
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
            <q-icon
              class="cursor-pointer"
              :name="showPasswordStatus ? 'mdi-eye' : 'mdi-eye-off'"
              @click="showPasswordStatus = !showPasswordStatus"
            />
          </template>
        </q-input>

        <div class="row justify-start q-mt-sm">
          <q-btn
            dense
            flat
            class="q-px-none text-caption"
            color="primary"
            to="/auth/forgot-password"
          >
            Forgot Password?
          </q-btn>
        </div>

        <div class="text-center q-mt-xl">
          <q-btn class="bg-blue full-width text-white q-px-lg q-mb-md" type="submit" :loading="loading">
            Login
          </q-btn>
          <!-- <div class="text-grey-7 q-mt-sm">
            Don't have an account?
            <q-btn
              dense
              flat
              class="q-px-sm"
              color="primary"
              to="/signup"
            >
              Sign up here
            </q-btn>
          </div> -->
        </div>
      </q-form>
    </div>

    <q-dialog v-model="showVerificationModal" persistent>
      <q-card style="min-width: 350px">
        <q-card-section class="row items-center">
          <div class="text-h6">
            Email Verification Required
          </div>
          <q-space />
          <q-btn
            v-close-popup
            dense
            flat
            round
            icon="close"
          />
        </q-card-section>

        <q-card-section class="q-pt-none">
          <p>Your email address needs to be verified before you can log in.</p>
          <p>We've sent a verification email to <strong>{{ state.email }}</strong></p>
          <p>Please check your inbox and click the verification link to complete the verification.</p>
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn
            flat
            :disable="resendCooldown > 0"
            :label="resendCooldown > 0 ? `Resend Email (${resendCooldown}s)` : 'Resend Email'"
            @click="handleResendVerification"
          />
          <q-btn v-close-popup flat label="OK" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>
