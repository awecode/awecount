<template>
  <div class="row justify-center items-center bg-white q-pa-md">
    <div class="full-width q-px-md">
      <q-form class="text-sm" @submit="onLoginSubmit" autofocus>
        <!-- <q-input label="Email" class="q-mb-lg" :hide-bottom-space="true"></q-input> -->
        <q-input v-model="username" label="Email" input-class="text-body1"
          :error="Boolean(errorMessage?.email ? true : false)" :error-message="errorMessage
            ? errorMessage.email
              ? errorMessage.email[0]
              : null
            : null
            ">
          <template v-slot:before>
            <q-icon name="fa-solid fa-envelope" />
          </template>
        </q-input>
        <q-input v-model="password" :type="showPasswordStatus ? 'text' : 'password'" label="Password"
          input-class="text-body1" :error="Boolean(errorMessage?.password ? true : false)" :error-message="errorMessage
            ? errorMessage.password
              ? errorMessage.password[0]
              : null
            : null
            ">
          <template v-slot:before>
            <q-icon name="fa-solid fa-lock" />
          </template>
          <template v-slot:append>
            <q-icon :name="showPasswordStatus ? 'mdi-eye' : 'mdi-eye-off'"
              @click="showPasswordStatus = !showPasswordStatus" class="cursor-pointer" />
          </template>
        </q-input>
        <div class="text-center q-mt-xl">
          <q-btn type="submit" class="bg-blue full-width text-white q-px-lg">Login</q-btn>
        </div>
      </q-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import useApi from '/src/composables/useApi'
import { useQuasar } from 'quasar'
import { useLoginStore } from '/src/stores/login-info.js'
import { useRouter } from 'vue-router'
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
    true
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
      console.log(err)
      errorMessage.value = err.response._data
      $q.notify({
        color: 'red-6',
        message:
          err.status == '500'
            ? 'Server Error! Please contact us with the problem.'
            : 'Please provide valid credentials.',
        icon: 'report_problem',
        position: 'top-right',
      })
    })
}
</script>

<style scoped></style>
