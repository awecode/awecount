<script setup lang="ts">
import { getGravatarUrl } from '@/utils/gravatar'
import { useQuasar } from 'quasar'

const step = ref(Number.parseInt(sessionStorage.getItem('onboarding-step') || '1'))

const route = useRoute()
const router = useRouter()
const { $api } = useNuxtApp()
const { switchCompany } = useAuth()

watch(step, (newStep) => {
  sessionStorage.setItem('onboarding-step', newStep.toString())
})

const savedState = sessionStorage.getItem('onboarding-state')
const state = reactive(
  savedState
    ? JSON.parse(savedState)
    : {
      // Basic Details
        companyName: '',
        country: null,
        currency: null,

        // Team Members
        teamMembers: [],
      },
)

watch(
  () => state,
  (newState) => {
    sessionStorage.setItem('onboarding-state', JSON.stringify(newState))
  },
  { deep: true },
)

const loading = ref(false)
const errors = ref({
  companyName: null,
  country: null,
  currency: null,
})

// Update the countries array to include more metadata
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

const roles = [
  { label: 'Admin', value: 'admin' },
  { label: 'Member', value: 'member' },
]

// Team member management
const newTeamMember = reactive({
  email: '',
  role: '',
})

const $q = useQuasar()

const validateEmail = (email: string) => {
  return email.match(
    /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\])|(([a-z\-0-9]+\.)+[a-z]{2,}))$/i,
  )
}

const addTeamMember = () => {
  if (!newTeamMember.email || !newTeamMember.role) return

  if (!validateEmail(newTeamMember.email)) {
    $q.notify({
      type: 'negative',
      message: 'Please enter a valid email address',
    })
    return
  }

  // Check for duplicate email
  if (state.teamMembers.some(member => member.email === newTeamMember.email)) {
    $q.notify({
      type: 'negative',
      message: 'This email has already been added',
    })
    return
  }

  state.teamMembers.push({
    email: newTeamMember.email,
    role: newTeamMember.role,
  })

  newTeamMember.email = ''
  newTeamMember.role = ''
}

const removeTeamMember = (index: number) => {
  state.teamMembers.splice(index, 1)
}

const validateStep = () => {
  errors.value = {
    companyName: null,
    country: null,
    currency: null,
  }

  if (step.value === 1) {
    if (!state.companyName) errors.value.companyName = 'Company name is required'
    if (!state.country) errors.value.country = 'Country is required'
    if (!state.currency) errors.value.currency = 'Currency is required'

    return !Object.values(errors.value).some(error => error !== null)
  }

  return true
}

// Add company slug ref to store after creation
const companySlug = ref('')

// Add these refs for setup progress
const setupProgress = ref(0)
const setupMessage = ref('')
const isSettingUp = ref(false)

const completeOnboarding = async () => {
  loading.value = true

  try {
    await $api('/api/user/me/onboarded/', { method: 'PATCH', body: { is_onboarded: true } })

    // Clear storage
    sessionStorage.removeItem('onboarding-state')
    sessionStorage.removeItem('onboarding-step')

    await switchCompany(companySlug.value, { router, route })
  } catch (err: any) {
    $q.notify({
      type: 'negative',
      message: err.response?.data?.message || 'Failed to complete onboarding. Please try again.',
    })
  } finally {
    loading.value = false
  }
}

const createCompany = async () => {
  if (!validateStep()) return

  loading.value = true
  try {
    const companyData = {
      name: state.companyName,
      country: countries.find(c => c.value === state.country)?.label,
      country_iso: state.country,
      currency_code: state.currency,
    }

    const res = await $api('/api/company/', { method: 'POST', body: companyData })
    companySlug.value = res.slug

    // Show initial success
    $q.notify({
      type: 'positive',
      message: 'Company created successfully!',
    })

    step.value = 2
  } catch (err: any) {
    console.error('Error in onboarding:', err)
    $q.notify({
      type: 'negative',
      message: err.response?.data?.message || 'Failed to create company. Please try again.',
    })
  } finally {
    loading.value = false
  }
}

const inviteTeamMembers = async () => {
  if (!validateStep()) return

  if (!state.teamMembers.length) return
  if (!companySlug.value) return

  loading.value = true
  try {
    const invitationData = {
      emails: state.teamMembers.map(member => ({
        email: member.email,
        role: member.role,
      })),
    }

    await $api(`/api/company/${companySlug.value}/invitations/`, { method: 'POST', body: invitationData })

    $q.notify({
      type: 'positive',
      message: 'Team members invited successfully! Redirecting to dashboard...',
    })

    completeOnboarding()
  } catch (err: any) {
    console.error('Error in onboarding:', err)
    $q.notify({
      type: 'negative',
      message: err.response?.data?.message || 'Failed to invite team members. You can invite them later from the dashboard.',
    })
  } finally {
    loading.value = false
  }
}

watch(() => state.country, (newCountry) => {
  if (newCountry) {
    const country = countries.find(c => c.value === newCountry)
    if (country?.defaults) {
      // Set currency and tax settings
      state.currency = country.defaults.currency
    }
  }
})

const showInviteForm = ref(false)
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
          Welcome to Awecount!
        </div>
        <div class="text-subtitle2 text-grey-7">
          Let's get your account set up
        </div>
      </q-card-section>

      <q-card-section>
        <q-stepper
          v-model="step"
          animated
          flat
          class="bg-white"
          color="primary"
        >
          <!-- Step 1: Basic Details -->
          <q-step
            icon="fa-solid fa-building"
            title="Basic Details"
            :done="step > 1"
            :name="1"
          >
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

            <q-stepper-navigation class="row justify-end">
              <q-btn
                color="primary"
                label="Continue"
                :loading="loading"
                @click="createCompany"
              />
            </q-stepper-navigation>
          </q-step>

          <!-- Step 2: Team Members -->
          <q-step icon="fa-solid fa-users" title="Team" :name="2">
            <div v-if="!state.teamMembers.length" class="text-center q-pa-md">
              <div class="text-h6 q-mb-md">
                Would you like to invite team members?
              </div>
              <div class="text-subtitle1 text-grey-7 q-mb-lg">
                You can invite your team members now or do it later from the dashboard
              </div>
              <div class="row justify-center q-gutter-md">
                <q-btn color="primary" label="Yes, Invite Team Members" @click="showInviteForm = true" />
                <q-btn
                  flat
                  color="primary"
                  label="Skip for Now"
                  @click="() => {
                    completeOnboarding()
                  }"
                />
              </div>
            </div>

            <template v-else>
              <div class="row items-center q-mb-lg">
                <div class="col">
                  <div class="text-h6">
                    Team Members
                  </div>
                  <div class="text-subtitle2 text-grey-7">
                    Invited team members will receive an email to join your company
                  </div>
                </div>
                <div class="col-auto">
                  <q-btn
                    color="primary"
                    icon="add"
                    label="Add Another"
                    @click="showInviteForm = true"
                  />
                </div>
              </div>

              <div class="row q-col-gutter-md">
                <div v-for="(member, index) in state.teamMembers" :key="index" class="col-md-6 col-12">
                  <q-card bordered flat>
                    <q-card-section>
                      <div class="row items-center">
                        <div class="col-auto">
                          <q-avatar size="48px">
                            <img :src="getGravatarUrl(member.email)" />
                          </q-avatar>
                        </div>
                        <div class="col q-ml-md">
                          <div class="text-subtitle1">
                            {{ member.email }}
                          </div>
                          <div class="text-caption">
                            {{ roles.find(r => r.value === member.role)?.label }}
                          </div>
                        </div>
                        <div class="col-auto">
                          <q-btn
                            flat
                            round
                            color="negative"
                            icon="delete"
                            @click="removeTeamMember(index)"
                          >
                            <q-tooltip>Remove</q-tooltip>
                          </q-btn>
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </template>

            <q-dialog v-model="showInviteForm">
              <q-card style="min-width: 350px">
                <q-card-section class="row items-center">
                  <div class="text-h6">
                    Invite Team Member
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
                  <div class="row q-col-gutter-md">
                    <div class="col-12">
                      <q-input
                        v-model="newTeamMember.email"
                        label="Email Address"
                        type="email"
                        :rules="[val => !!val || 'Email is required']"
                      />
                    </div>

                    <div class="col-12">
                      <q-select
                        v-model="newTeamMember.role"
                        emit-value
                        map-options
                        label="Role"
                        :options="roles"
                        :rules="[val => !!val || 'Role is required']"
                      />
                    </div>
                  </div>
                </q-card-section>

                <q-card-actions align="right">
                  <q-btn
                    v-close-popup
                    flat
                    color="primary"
                    label="Cancel"
                  />
                  <q-btn
                    color="primary"
                    label="Add"
                    :disable="!newTeamMember.email || !newTeamMember.role"
                    @click="() => {
                      addTeamMember()
                      showInviteForm = false
                    }"
                  />
                </q-card-actions>
              </q-card>
            </q-dialog>

            <q-stepper-navigation class="row justify-end q-mt-lg">
              <q-btn
                v-if="state.teamMembers.length"
                color="primary"
                label="Complete Setup"
                :loading="loading"
                @click="inviteTeamMembers"
              />
            </q-stepper-navigation>
          </q-step>
        </q-stepper>
      </q-card-section>

      <!-- Add setup progress dialog -->
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
