<script setup lang="ts">
import { useQuasar } from 'quasar'

import { computed, reactive, ref as vueRef } from 'vue'
import { useRouter } from 'vue-router'

const $q = useQuasar()
const router = useRouter()

const { $api } = useNuxtApp()
const { hasRole } = useAuth()

// Options for dropdowns
const companyTypes = [
  { label: 'Private Limited', value: 'private_limited' },
  { label: 'Public Limited', value: 'public_limited' },
  { label: 'Sole Proprietorship', value: 'sole_proprietorship' },
  { label: 'Partnership', value: 'partnership' },
  { label: 'Corporation', value: 'corporation' },
  { label: 'Non-profit', value: 'non_profit' },
]

const countries = [
  {
    label: 'Nepal',
    value: 'NP',
    defaults: {
      currency: 'NPR',
    },
  },
  {
    label: 'India',
    value: 'IN',
    defaults: {
      currency: 'INR',
    },
  },
  {
    label: 'United States',
    value: 'US',
    defaults: {
      currency: 'USD',
    },
  },
  // Add more countries as needed
]

// Update the currencies array to include more metadata
const currencies = [
  { label: 'Nepalese Rupee (NPR)', value: 'NPR', symbol: 'रू' },
  { label: 'Indian Rupee (INR)', value: 'INR', symbol: '₹' },
  { label: 'US Dollar (USD)', value: 'USD', symbol: '$' },
  // Add more currencies as needed
]

// Company settings state
const state = reactive({
  name: '',
  taxIdentificationNumber: '', // Renamed here
  organization_type: null,
  country: null,
  currency: null,
})

const loading = ref(false)
const errors = ref({
  name: null,
  taxIdentificationNumber: null, // Renamed here
  organization_type: null,
  country: null,
  currency: null,
})

// Company logo handling
const logoInput = vueRef<HTMLInputElement | null>(null)
const logoPreview = ref('')

// Add computed for fallback letter
const companyInitial = computed(() => {
  return state.name ? state.name.charAt(0).toUpperCase() : 'C'
})

// Load company data
const loadCompanyData = async () => {
  loading.value = true
  try {
    const data = await $api(`/api/company/${router.currentRoute.value.params.company}/`)
    state.name = data.name
    state.taxIdentificationNumber = data.tax_identification_number // Renamed here
    state.organization_type = data.organization_type
    state.country = data.country_iso
    state.currency = data.currency_code
    logoPreview.value = data.logo || '' // Remove gravatar fallback
  } catch (err) {
    console.error('Failed to load company data:', err)
    $q.notify({
      type: 'negative',
      message: 'Failed to load company data',
    })
  } finally {
    loading.value = false
  }
}

// Handle logo upload
const handleLogoUpload = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  // Preview
  const reader = new FileReader()
  reader.onload = (e) => {
    logoPreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)

  // Upload
  try {
    const formData = new FormData()
    formData.append('logo', file)

    await $api(`/api/company/${router.currentRoute.value.params.company}/upload-logo/`, {
      method: 'POST',
      body: formData,
    })

    $q.notify({
      type: 'positive',
      message: 'Company logo updated successfully',
    })
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Failed to update company logo',
    })
  }
}

// Update company
const updateCompany = async () => {
  loading.value = true
  try {
    await $api(`/api/company/${router.currentRoute.value.params.company}/`, {
      method: 'PATCH',
      body: {
        name: state.name,
        tax_identification_number: state.taxIdentificationNumber, // Renamed here
        organization_type: state.organization_type,
        country_iso: state.country,
        currency_code: state.currency,
      },
    })

    $q.notify({
      type: 'positive',
      message: 'Company updated successfully',
    })
  } catch (err: any) {
    if (err.response?.data?.errors) {
      errors.value = err.response.data.errors
    } else {
      $q.notify({
        type: 'negative',
        message: 'Failed to update company',
      })
    }
  } finally {
    loading.value = false
  }
}

// Add these refs after other refs
const deleteDialog = ref(false)
const deleteConfirmation = ref('')
const companySlug = computed(() => router.currentRoute.value.params.company as string)

// Add this method after other methods
const deleteCompany = async () => {
  if (deleteConfirmation.value !== companySlug.value) return

  loading.value = true
  try {
    await $api(`/api/company/${companySlug.value}/`, {
      method: 'DELETE',
    })

    $q.notify({
      type: 'positive',
      message: 'Company deleted successfully',
    })

    // Redirect to home page
    router.push('/')
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Failed to delete company',
    })
  } finally {
    loading.value = false
    deleteDialog.value = false
  }
}

onMounted(() => {
  loadCompanyData()
})
</script>

<template>
  <div>
    <!-- Company Banner -->
    <div class="company-banner q-mb-xl">
      <div class="banner-content">
        <div class="row items-center">
          <div class="col-auto">
            <div class="logo-container">
              <!-- Show logo or fallback to initial letter -->
              <template v-if="logoPreview">
                <q-img class="company-logo" :src="logoPreview">
                  <template #error>
                    <div class="company-logo company-logo--fallback">
                      {{ companyInitial }}
                    </div>
                  </template>
                </q-img>
              </template>
              <template v-else>
                <div class="company-logo company-logo--fallback">
                  {{ companyInitial }}
                </div>
              </template>

              <q-btn
                dense
                flat
                round
                class="edit-logo-btn"
                color="grey-8"
                icon="edit"
                @click="logoInput?.click()"
              >
                <q-tooltip>Change Logo</q-tooltip>
              </q-btn>
              <input
                ref="logoInput"
                accept="image/*"
                class="hidden"
                type="file"
                @change="handleLogoUpload"
              />
            </div>
          </div>
          <div class="col q-pl-md">
            <div class="text-h5">
              {{ state.name }}
            </div>
            <div class="text-caption text-grey-7">
              {{ state.organization_type ? companyTypes.find(t => t.value === state.organization_type)?.label
                : 'Company' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Company Information -->
    <div class="text-subtitle1 q-mb-md">
      Company Information
    </div>
    <div class="row q-col-gutter-md">
      <div class="col-12">
        <q-input
          v-model="state.name"
          dense
          outlined
          label="Company Name"
          :error="!!errors.name"
          :error-message="errors.name"
        />
      </div>
      <div class="col-12">
        <q-input
          v-model="state.taxIdentificationNumber"
          dense
          outlined
          label="Tax Identification Number"
          :error="!!errors.taxIdentificationNumber"
          :error-message="errors.taxIdentificationNumber"
        />
      </div>
      <div class="col-12">
        <q-select
          v-model="state.organization_type"
          dense
          emit-value
          map-options
          outlined
          label="Company Type"
          :error="!!errors.organization_type"
          :error-message="errors.organization_type"
          :options="companyTypes"
        />
      </div>
      <div class="col-md-6 col-12">
        <q-select
          v-model="state.country"
          dense
          emit-value
          map-options
          outlined
          label="Country"
          :error="!!errors.country"
          :error-message="errors.country"
          :options="countries"
        />
      </div>
      <div class="col-md-6 col-12">
        <q-select
          v-model="state.currency"
          dense
          emit-value
          map-options
          outlined
          label="Currency"
          :error="!!errors.currency"
          :error-message="errors.currency"
          :options="currencies"
        />
      </div>
    </div>
    <div class="row justify-end q-mt-md">
      <q-btn
        unelevated
        color="primary"
        label="Update Company"
        :loading="loading"
        @click="updateCompany"
      />
    </div>

    <template v-if="hasRole('owner')">
      <q-separator class="q-my-lg" />

      <div class="text-subtitle1 q-mb-md">
        Danger Zone
      </div>
      <div :style="{ border: '1px solid #FF6467', backgroundColor: '#FFECEC', borderRadius: '8px', padding: '16px' }">
        <div :style="{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }">
          <div>
            <div class="text-subtitle2 text-weight-medium">
              Delete this company
            </div>
            <div class="text-caption text-grey-7">
              Once deleted, the company and all of its resources will be permanently removed and cannot be recovered.
            </div>
          </div>
          <q-btn
            unelevated
            color="negative"
            label="Delete Company"
            @click="deleteDialog = true"
          />
        </div>
      </div>

      <q-dialog v-model="deleteDialog" persistent>
        <q-card style="min-width: 350px">
          <q-card-section class="row items-center">
            <div class="text-h6">
              Delete Company
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

          <q-card-section>
            <p class="text-body1 q-mb-md">
              This action cannot be undone. This will permanently delete the
              <strong>{{ state.name }}</strong> company and all of its data.
            </p>
            <p class="text-body2 q-mb-md">
              Please type <strong>{{ companySlug }}</strong> to confirm.
            </p>
            <q-input
              v-model="deleteConfirmation"
              dense
              outlined
              placeholder="Type company slug to confirm"
              :error="deleteConfirmation && deleteConfirmation !== companySlug"
              :error-message="deleteConfirmation && deleteConfirmation !== companySlug ? 'Company slug does not match' : ''"
            />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn
              v-close-popup
              flat
              color="primary"
              label="Cancel"
            />
            <q-btn
              flat
              color="negative"
              label="Delete Company"
              :disable="deleteConfirmation !== companySlug"
              :loading="loading"
              @click="deleteCompany"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </template>
  </div>
</template>

<style scoped>
.q-input {
  background: white;
}

:deep(.q-field--outlined .q-field__control) {
  background: white;
}

:deep(.q-field--outlined .q-field__control:hover) {
  border-color: var(--q-primary);
}

.bg-white {
  background: white;
}

/* Update active item style to match Plane */
:deep(.q-item.active) {
  color: var(--q-primary);
  background: #EEF2FF;
  font-weight: 500;
}

/* Style for list padding */
:deep(.q-list--padding) {
  padding: 4px 0;
}

/* Reduce item padding */
:deep(.q-item) {
  padding: 8px 12px;
  min-height: 36px;
  border-radius: 4px;
  font-size: 14px;
}

/* Reduce avatar size */
:deep(.q-item__section--avatar) {
  min-width: 24px;
  padding-right: 12px;
}

/* Style for icons */
:deep(.q-icon) {
  font-size: 20px;
}

.company-banner {
  background: linear-gradient(to right, #f7f7f7, #ffffff);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.banner-content {
  padding: 24px;
}

.logo-container {
  position: relative;
  width: 80px;
  height: 80px;
}

.company-logo {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.company-logo--fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--q-primary) 0%, #4F46E5 100%);
  color: white;
  font-size: 32px;
  font-weight: 500;
}

.edit-logo-btn {
  position: absolute;
  right: -8px;
  bottom: -8px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.hidden {
  display: none;
}

.q-list {
  border-radius: 8px;
  background: white;
}
</style>
