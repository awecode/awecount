<script setup>
import { useQuasar } from 'quasar'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import useApi from '/src/composables/useApi'
import { useLoginStore } from '/src/stores/login-info.js'

const router = useRouter()
const loginStore = useLoginStore()
const $q = useQuasar()
const showPasswordStatus = ref(false)
const username = ref(null)
const password = ref(null)
const errorMessage = ref(null)
const onLoginSubmit = async () => {
  // console.log('Hi')
  errorMessage.value = null
  await useApi(
    'v1/auth/login/',
    {
      method: 'POST',
      body: { email: username.value, password: password.value },
    },
    true,
  )
    .then((data) => {
      loginStore.token = data.access
      loginStore.username = data.user.full_name
      loginStore.email = data.user.email
      loginStore.companyInfo = data.company
      loginStore.userInfo = data.user
      loginStore.companyInfo.logo_url = data.company.logo_url || '/img/stockCompany.png'
      if (data.company.config_template !== 'np') {
        loginStore.isCalendarInAD = true
      }
      router.push('/dashboard')
    })
    .catch((err) => {
      $q.notify({
        color: 'red-6',
        message: [401, 400].includes(err?.status) ? 'Please provide valid credentials.' : 'Server Error! Please contact us with the problem.',
        icon: 'report_problem',
        position: 'top-right',
      })
    })
}
</script>

<template>
  <div class="row justify-center items-center bg-white q-pa-md">
    <div class="full-width q-px-md">
      <q-form autofocus class="text-sm" @submit="onLoginSubmit">
        <!-- <q-input label="Email" class="q-mb-lg" :hide-bottom-space="true"></q-input> -->
        <q-input
          v-model="username"
          input-class="text-body1"
          label="Email"
          :error="Boolean(errorMessage?.email ? true : false)"
          :error-message="
            errorMessage
              ? errorMessage.email
                ? errorMessage.email[0]
                : null
              : null
          "
        >
          <template #before>
            <q-icon name="fa-solid fa-envelope" />
          </template>
        </q-input>
        <q-input
          v-model="password"
          input-class="text-body1"
          label="Password"
          :error="Boolean(errorMessage?.password ? true : false)"
          :error-message="
            errorMessage
              ? errorMessage.password
                ? errorMessage.password[0]
                : null
              : null
          "
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
          <q-btn class="bg-blue full-width text-white q-px-lg" type="submit">
            Login
          </q-btn>
        </div>
      </q-form>
    </div>
  </div>
</template>
