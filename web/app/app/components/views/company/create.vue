<script setup lang="ts">
import { useQuasar } from 'quasar'
import { useRouter } from 'vue-router'

const $q = useQuasar()
const route = useRoute()
const router = useRouter()

const { $api } = useNuxtApp()
const { switchCompany } = useAuth()

// Company creation state
const state = reactive({
  companyName: '',
  country: null,
  currency: null,
})

const loading = ref(false)
const setupProgress = ref(0)
const setupMessage = ref('')
const isSettingUp = ref(false)

const errors = ref({
  companyName: null,
  country: null,
  currency: null,
})

// Options for dropdowns (same as onboarding)
const countries = [
  {
    label: 'Nepal',
    value: 'NP',
    defaults: { currency: 'NPR' },
  },
  {
    label: 'India',
    value: 'IN',
    defaults: { currency: 'INR' },
  },
  {
    label: 'United States',
    value: 'US',
    defaults: { currency: 'USD' },
  },
]

const currencies = [
  { label: 'Nepalese Rupee (NPR)', value: 'NPR' },
  { label: 'Indian Rupee (INR)', value: 'INR' },
  { label: 'US Dollar (USD)', value: 'USD' },
]

// Watch for country changes to set default currency
watch(() => state.country, (newCountry) => {
  if (newCountry) {
    const country = countries.find(c => c.value === newCountry)
    if (country?.defaults) {
      state.currency = country.defaults.currency
    }
  }
})

// Create company
const createCompany = async () => {
  // Validate
  errors.value = {
    companyName: !state.companyName ? 'Company name is required' : null,
    country: !state.country ? 'Country is required' : null,
    currency: !state.currency ? 'Currency is required' : null,
  }

  if (Object.values(errors.value).some(error => error !== null)) return

  loading.value = true
  try {
    const companyData = {
      name: state.companyName,
      country: countries.find(c => c.value === state.country)?.label || null,
      country_iso: state.country,
      currency_code: state.currency,
    }

    const data = await $api('/api/company/', {
      method: 'POST',
      body: companyData,
    })

    $q.notify({
      type: 'positive',
      message: 'Company created successfully!',
    })

    await switchCompany(data.slug, { router, route })
  } catch (err: any) {
    if (err.response?.data?.errors) {
      const apiErrors = err.response.data.errors
      errors.value = {
        companyName: apiErrors.name?.[0] || null,
        country: apiErrors.country?.[0] || null,
        currency: apiErrors.currency?.[0] || null,
      }
    } else {
      $q.notify({
        type: 'negative',
        message: err.response?.data?.message || 'Failed to create company. Please try again.',
      })
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="window-height onboarding-background row justify-center items-center">
    <div class="onboarding-container q-pa-lg">
      <q-card-section class="text-center">
        <div class="row justify-center">
          <img
            alt="Awecount"
            class="q-mb-md"
            src="/img/awecount.png"
            style="width: 80px; height: 80px;"
          />
        </div>
        <div class="text-h5">
          Create New Company
        </div>
        <div class="text-subtitle2 text-grey-7">
          Enter your company details below
        </div>
      </q-card-section>

      <q-card-section>
        <div class="row q-col-gutter-md">
          <div class="col-12">
            <q-input
              v-model="state.companyName"
              label="Company Name *"
              :error="!!errors.companyName"
              :error-message="errors.companyName"
            />
          </div>

          <div class="col-md-6 col-12">
            <q-select
              v-model="state.country"
              emit-value
              map-options
              label="Country *"
              :error="!!errors.country"
              :error-message="errors.country"
              :options="countries"
            />
          </div>

          <div class="col-md-6 col-12">
            <q-select
              v-model="state.currency"
              emit-value
              map-options
              label="Currency *"
              :error="!!errors.currency"
              :error-message="errors.currency"
              :options="currencies"
            />
          </div>
        </div>
      </q-card-section>

      <q-card-section>
        <div class="row justify-end q-gutter-sm">
          <q-btn
            flat
            color="primary"
            label="Cancel"
            @click="router.back()"
          />
          <q-btn
            color="primary"
            label="Create Company"
            :loading="loading"
            @click="createCompany"
          />
        </div>
      </q-card-section>
    </div>

    <!-- Setup Progress Dialog -->
    <q-dialog v-model="isSettingUp" persistent>
      <q-card style="min-width: 300px">
        <q-card-section class="row items-center">
          <div class="text-h6">
            Setting Up Your Company
          </div>
        </q-card-section>

        <q-card-section>
          <div class="text-subtitle1 q-mb-md">
            {{ setupMessage }}
          </div>
          <q-linear-progress class="q-mt-md" color="primary" :value="setupProgress / 100" />
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped>
.onboarding-background {
  background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
  position: relative;
  overflow: hidden;
}

.onboarding-background::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
  pointer-events: none;
}

.onboarding-container {
  width: 90%;
  max-width: 800px;
  background: rgba(255, 255, 255);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(8px);
  z-index: 1;
}

@media (max-width: 600px) {
  .onboarding-container {
    width: 95%;
    padding: 16px !important;
  }
}
</style>
