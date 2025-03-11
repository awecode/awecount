<script setup lang="ts">
import { useQuasar } from 'quasar'
import { useAuthStore } from 'stores/auth'
import { reactive, ref } from 'vue'

const emit = defineEmits<{
  signedUp: [Record<string, any>]
}>()

const $q = useQuasar()
const { signup, requestEmailVerification, checkEmail } = useAuthStore()

const showPasswordStatus = ref(false)
const loading = ref(false)
const showVerificationModal = ref(false)

const state = reactive({
  email: null,
  password: null,
})

const errors = ref({
  email: null,
  password: null,
})

const handleSignupError = (error: any) => {
  const errorResponse: any = error.data || error.response?._data

  if (errorResponse.status === 401) {
    const flows = errorResponse.data?.flows || []
    const verifyEmailFlow = flows.find((flow: any) => flow.id === 'verify_email')

    if (verifyEmailFlow && verifyEmailFlow.is_pending) {
      showVerificationModal.value = true
      return
    }
  }

  if (errorResponse?.errors?.[0]) {
    const firstError = errorResponse.errors[0]
    if (firstError.param) {
      errors.value[firstError.param] = firstError.message
      return
    }
  }

  $q.notify({
    position: 'top-right',
    message: 'Signup Failed',
    caption: error.message || 'Please try again later',
    color: 'negative',
    icon: 'fa-solid fa-circle-exclamation',
  })

  console.error(error)
}

const onSignupSubmit = async () => {
  try {
    loading.value = true
    const { data } = await checkEmail(state.email)
    if (data.existing) {
      errors.value.email = 'User already exists'
      return
    }
    const res = await signup(state)
    showVerificationModal.value = true
    emit('signedUp', res)
  } catch (error: any) {
    handleSignupError(error)
  } finally {
    loading.value = false
  }
}

const handleResendVerification = async () => {
  try {
    if (!state.email) return
    await requestEmailVerification(state.email)
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
</script>

<template>
  <div class="row justify-center items-center bg-white q-pa-md">
    <div class="full-width q-px-md">
      <q-form autofocus class="text-sm" @submit="onSignupSubmit">
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

        <div class="text-center q-mt-xl">
          <q-btn class="bg-blue full-width text-white q-px-lg q-mb-md" type="submit" :loading="loading">
            Sign Up
          </q-btn>
          <div class="text-grey-7 q-mt-sm">
            Already have an account?
            <q-btn
              dense
              flat
              class="q-px-sm"
              color="primary"
              to="/login"
            >
              Login here
            </q-btn>
          </div>
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
          <p>We've sent a verification email to <strong>{{ state.email }}</strong></p>
          <p>Please check your inbox and click the verification link to complete your registration.</p>
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Resend Email" @click="handleResendVerification" />
          <q-btn
            v-close-popup
            flat
            label="OK"
            @click="() => {
              showVerificationModal = false
              $router.push('/login')
            }"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>
