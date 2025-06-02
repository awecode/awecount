<script setup lang="ts">
import { useQuasar } from 'quasar'
import { $api } from 'src/composables/api'
import { useAuthStore } from 'src/stores/auth'
import { getGravatarUrl } from 'src/utils/gravatar'
import { useRouter } from 'vue-router'

const $q = useQuasar()
const router = useRouter()
const { changePassword: authChangePassword, refreshUser, logout, switchCompany } = useAuthStore()

// User profile state
const state = reactive({
  fullName: '',
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const loading = ref(false)
const errors = ref({
  fullName: null,
  firstName: null,
  lastName: null,
  email: null,
  phone: null,
  currentPassword: null,
  newPassword: null,
  confirmPassword: null,
})

// Add companies state
const companies = ref([])

// Add these refs for the confirmation dialog
const showDeactivateDialog = ref(false)
const confirmEmail = ref('')
const deactivateLoading = ref(false)

// Add validation computed property
const isEmailConfirmed = computed(() => {
  return confirmEmail.value === state.email
})

// Load user data
const loadUserProfile = async () => {
  loading.value = true
  try {
    const data = await $api('/api/user/me/')
    state.fullName = data.full_name
    state.firstName = data.first_name
    state.lastName = data.last_name
    state.email = data.email
    state.phone = data.phone_number
  } catch (err: any) {
    console.error('Failed to load profile data:', err)
    $q.notify({
      type: 'negative',
      message: 'Failed to load profile data',
    })
  } finally {
    loading.value = false
  }
}

// Load companies
const loadCompanies = async () => {
  try {
    const data = await $api('/api/user/me/companies/')
    companies.value = data
  } catch (err) {
    console.error('Failed to load companies:', err)
  }
}

// Update profile
const updateProfile = async () => {
  loading.value = true
  try {
    await $api('/api/user/me/', {
      method: 'PATCH',
      body: {
        full_name: state.fullName,
        phone_number: state.phone,
      },
    })

    $q.notify({
      type: 'positive',
      message: 'Profile updated successfully',
    })

    await refreshUser()
  } catch (err: any) {
    if (err.response?.data?.errors) {
      errors.value = err.response.data.errors
    } else {
      $q.notify({
        type: 'negative',
        message: 'Failed to update profile',
      })
    }
  } finally {
    loading.value = false
  }
}

// Change password
const changePassword = async () => {
  if (state.newPassword !== state.confirmPassword) {
    errors.value.confirmPassword = 'Passwords do not match'
    return
  }

  loading.value = true
  try {
    await authChangePassword({
      current_password: state.currentPassword,
      new_password: state.newPassword,
    })

    $q.notify({
      type: 'positive',
      message: 'Password changed successfully',
    })

    // Clear password fields
    state.currentPassword = ''
    state.newPassword = ''
    state.confirmPassword = ''
  } catch (err: any) {
    if (err.response?.data?.errors) {
      errors.value = err.response.data.errors
    } else {
      $q.notify({
        type: 'negative',
        message: 'Failed to change password',
      })
    }
  } finally {
    loading.value = false
  }
}

const deactivateAccount = async () => {
  await $api('/api/user/me/deactivate/', {
    method: 'PATCH',
  })

  $q.notify({
    type: 'positive',
    message: 'Account deactivated successfully',
  })

  await logout({ redirectTo: '/login' })
}

// Modify the deactivate function to handle the confirmation flow
const confirmDeactivation = async () => {
  if (!isEmailConfirmed.value) {
    $q.notify({
      type: 'negative',
      message: 'Please enter your email correctly to confirm',
    })
    return
  }

  deactivateLoading.value = true
  try {
    await deactivateAccount()
    showDeactivateDialog.value = false
    confirmEmail.value = ''
  } finally {
    deactivateLoading.value = false
  }
}

// Load profile data on mount
onMounted(() => {
  loadUserProfile()
  loadCompanies()
})
</script>

<template>
  <div class="row no-wrap">
    <!-- Sidebar -->
    <div class="bg-white" style="width: 240px; border-right: 1px solid #e5e7eb; height: 100vh">
      <div class="column full-height">
        <!-- Header with back button -->
        <div class="q-px-md q-pt-md row items-center q-mb-md">
          <q-btn
            dense
            flat
            round
            color="primary"
            icon="arrow_back"
            @click="router.back()"
          />
          <div class="text-subtitle1 q-ml-sm">
            Profile settings
          </div>
        </div>

        <!-- Navigation Links -->
        <div class="q-px-md">
          <div class="text-caption text-grey-7 q-mb-sm">
            Your account
          </div>
          <q-list padding>
            <q-item v-ripple active clickable>
              <q-item-section avatar>
                <q-icon name="person_outline" />
              </q-item-section>
              <q-item-section>Profile</q-item-section>
            </q-item>

            <!-- <q-item v-ripple clickable>
              <q-item-section avatar>
                <q-icon name="security" />
              </q-item-section>
              <q-item-section>Security</q-item-section>
            </q-item> -->

            <q-item v-ripple clickable to="/invitations">
              <q-item-section avatar>
                <q-icon name="mail_outline" />
              </q-item-section>
              <q-item-section>Invitations</q-item-section>
            </q-item>
          </q-list>

          <div class="text-caption text-grey-7 q-mt-md q-mb-sm">
            Companies
          </div>
          <q-list padding>
            <q-item
              v-for="company in companies"
              :key="company.slug"
              v-ripple
              clickable
              @click="() => switchCompany(company.slug)"
            >
              <q-item-section avatar>
                <q-avatar color="primary" size="24px" text-color="white">
                  {{ company.name[0].toUpperCase() }}
                </q-avatar>
              </q-item-section>
              <q-item-section>{{ company.name }}</q-item-section>
            </q-item>

            <q-item v-ripple clickable @click="router.push('/company/create')">
              <q-item-section avatar>
                <q-icon name="add" />
              </q-item-section>
              <q-item-section>Create company</q-item-section>
            </q-item>
          </q-list>
        </div>

        <!-- Spacer -->
        <div class="col"></div>

        <!-- Footer with Sign Out -->
        <div class="q-px-md q-pb-md">
          <q-item
            v-ripple
            clickable
            class="text-negative"
            @click="() => logout({ redirectTo: '/login' })"
          >
            <q-item-section avatar>
              <q-icon color="negative" name="logout" />
            </q-item-section>
            <q-item-section>Sign out</q-item-section>
          </q-item>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="col">
      <!-- Navigation Header -->
      <div class="bg-white q-px-md" style="border-bottom: 1px solid #e5e7eb">
        <div class="row items-center" style="height: 64px">
          <div class="col">
            <div class="text-h6">
              Profile Settings
            </div>
          </div>
        </div>
      </div>

      <!-- Rest of the content -->
      <div class="q-pa-md">
        <div class="row justify-center q-mt-md">
          <div class="col-12" style="max-width: 600px">
            <!-- Profile Header -->
            <div class="row items-center q-mb-lg">
              <div class="col-auto">
                <q-avatar size="64px">
                  <img :src="getGravatarUrl(state.email)" />
                </q-avatar>
              </div>
              <div class="col q-ml-md">
                <div class="text-subtitle1 text-weight-medium">
                  {{ state.fullName }}
                </div>
                <div class="text-caption text-grey-7">
                  {{ state.email }}
                </div>
              </div>
            </div>

            <!-- Personal Information -->
            <div class="text-subtitle1 q-mb-md">
              Personal Information
            </div>
            <div class="row q-col-gutter-md">
              <div class="col-12">
                <q-input
                  v-model="state.fullName"
                  dense
                  outlined
                  label="Name"
                  :error="!!errors.fullName"
                  :error-message="errors.fullName"
                />
              </div>
              <div class="col-md-6 col-12">
                <q-input
                  v-model="state.email"
                  dense
                  outlined
                  readonly
                  label="Email"
                  type="email"
                  :error="!!errors.email"
                  :error-message="errors.email"
                />
              </div>
              <div class="col-md-6 col-12">
                <q-input
                  v-model="state.phone"
                  dense
                  outlined
                  label="Phone"
                  :error="!!errors.phone"
                  :error-message="errors.phone"
                />
              </div>
            </div>
            <div class="row justify-end q-mt-md">
              <q-btn
                unelevated
                color="primary"
                label="Update Profile"
                :loading="loading"
                @click="updateProfile"
              />
            </div>

            <q-separator class="q-my-lg" />

            <!-- Change Password -->
            <div class="text-subtitle1 q-mb-md">
              Change Password
            </div>
            <div class="row q-col-gutter-md">
              <div class="col-12">
                <q-input
                  v-model="state.currentPassword"
                  dense
                  outlined
                  label="Current Password"
                  type="password"
                  :error="!!errors.currentPassword"
                  :error-message="errors.currentPassword"
                />
              </div>
              <div class="col-md-6 col-12">
                <q-input
                  v-model="state.newPassword"
                  dense
                  outlined
                  label="New Password"
                  type="password"
                  :error="!!errors.newPassword"
                  :error-message="errors.newPassword"
                />
              </div>
              <div class="col-md-6 col-12">
                <q-input
                  v-model="state.confirmPassword"
                  dense
                  outlined
                  label="Confirm New Password"
                  type="password"
                  :error="!!errors.confirmPassword"
                  :error-message="errors.confirmPassword"
                />
              </div>
            </div>
            <div class="row justify-end q-mt-md">
              <q-btn
                unelevated
                color="primary"
                label="Change Password"
                :disable="!state.currentPassword || !state.newPassword || !state.confirmPassword"
                :loading="loading"
                @click="changePassword"
              />
            </div>

            <q-separator class="q-my-lg" />

            <!-- Deactivate Account -->
            <div class="text-subtitle1 q-mb-md">
              Deactivate Account
            </div>
            <div class="text-caption text-grey-7">
              When deactivating an account, all of the data and resources within that account will be permanently
              removed and cannot be recovered.
            </div>
            <div class="row q-mt-md">
              <q-btn
                unelevated
                color="negative"
                label="Deactivate Account"
                :loading="loading"
                @click="showDeactivateDialog = true"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Confirmation Dialog -->
  <q-dialog v-model="showDeactivateDialog" persistent>
    <q-card style="min-width: 350px">
      <q-card-section class="row items-center">
        <div class="text-h6">
          Confirm Account Deactivation
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
        <p class="text-negative">
          Warning: This action cannot be undone!
        </p>
        <p>To confirm account deactivation, please enter your email address:</p>
        <p class="text-weight-bold q-mb-sm">
          {{ state.email }}
        </p>

        <q-input
          v-model="confirmEmail"
          dense
          outlined
          label="Confirm Email"
          type="email"
          :error="confirmEmail !== '' && !isEmailConfirmed"
          :error-message="confirmEmail !== '' && !isEmailConfirmed ? 'Email does not match' : ''"
        />
      </q-card-section>

      <q-card-actions align="right" class="text-primary">
        <q-btn v-close-popup flat label="Cancel" />
        <q-btn
          flat
          color="negative"
          label="Deactivate Account"
          :disable="!isEmailConfirmed"
          :loading="deactivateLoading"
          @click="confirmDeactivation"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
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

/* Remove back button margin since we have sidebar now */
.text-h6 {
  margin-left: 0 !important;
}
</style>
