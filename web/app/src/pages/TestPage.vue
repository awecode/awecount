<template>
  <q-page class="q-pa-md">
    <div class="q-gutter-md">
      <q-form @submit.prevent="login" class="q-mt-xl">
        <q-input
          v-model="email"
          :error-label="emailError"
          label="Email"
          type="email"
          required
          class="q-mb-md"
        />
        <q-input
          v-model="password"
          label="Password"
          type="password"
          required
          class="q-mb-md"
        />
        <div class="q-mt-md q-mb-lg">
          <q-btn type="submit" label="Login" color="primary" class="q-mr-md" />
          <q-btn label="Clear" type="reset" color="secondary" />
        </div>
      </q-form>
      <q-dialog v-model="errorDialog" persistent>
        <q-card>
          <q-card-section>
            <q-card-title class="text-negative">Error</q-card-title>
            <q-card-text>{{ errorMessage }}</q-card-text>
          </q-card-section>
          <q-card-actions align="right">
            <q-btn
              label="Close"
              color="negative"
              @click="errorDialog = false"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
const email = ref('')
const password = ref('')
const errorDialog = false
const errorMessage = ''
const emailError = ''

const login = async () => {
  try {
    const response = await fetch('http://localhost:8000/v1/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    })
    if (response.ok) {
      // successful login logic here
    } else {
      const error = await response.json()
      if (error && error.email) {
        emailError = error.email
      }
      throw new Error('Login failed')
    }
  } catch (error) {
    errorMessage = error.message
    errorDialog = true
  }
}
</script>

<style lang="scss">
.q-card {
  width: 400px;
  max-width: 100%;
}
</style>
