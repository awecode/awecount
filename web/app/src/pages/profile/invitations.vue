<script setup lang="ts">
import { useQuasar } from 'quasar'
import { $api } from 'src/composables/api'
import { useRouter } from 'vue-router'

const $q = useQuasar()
const router = useRouter()

// Add invitation state
interface Invitation {
  id: string
  company: {
    name: string
    slug: string
  }
  role: string
  created_at: string
}

const invitations = ref<Invitation[]>([])
const loading = ref(false)

// Load invitations
const loadInvitations = async () => {
  loading.value = true
  try {
    const response = await $api('/api/user/me/invitations/')
    invitations.value = response
  } catch (err) {
    console.error('Failed to load invitations:', err)
    $q.notify({
      type: 'negative',
      message: 'Failed to load invitations',
    })
  } finally {
    loading.value = false
  }
}

// Handle invitation response
const respondToInvitation = async (accept: boolean) => {
  if (!invitations.value.length) return

  try {
    await $api('/api/user/me/invitations/', {
      method: 'POST',
      body: {
        invitations: invitations.value.map(inv => inv.id),
      },
    })

    $q.notify({
      type: 'positive',
      message: `Invitation ${accept ? 'accepted' : 'declined'} successfully`,
    })

    if (accept) {
      // Redirect to the first company
      const company = invitations.value[0].company.slug
      router.push(`/${company}/dashboard`)
    } else {
      router.push('/profile')
    }
  } catch (err) {
    console.error('Failed to respond to invitation:', err)
    $q.notify({
      type: 'negative',
      message: 'Failed to respond to invitation',
    })
  }
}

onMounted(() => {
  loadInvitations()
})
</script>

<template>
  <div class="onboarding-background column items-center justify-center">
    <div class="onboarding-container q-pa-xl">
      <!-- Logo -->
      <div class="row justify-center q-mb-xl">
        <q-img src="/logo.svg" width="120px" />
      </div>

      <!-- Content -->
      <div v-if="invitations.length > 0">
        <div class="text-h6 text-center q-mb-xl">
          We see that someone has invited you to
        </div>

        <div class="text-h5 text-center q-mb-xl">
          Join a workspace
        </div>

        <div class="workspace-list q-mb-xl">
          <div v-for="invite in invitations" :key="invite.id" class="workspace-item q-pa-md q-mb-sm">
            <div class="row items-center">
              <!-- Company Initial -->
              <div class="company-avatar">
                {{ invite.company.name.charAt(0).toUpperCase() }}
              </div>
              <div class="col q-ml-md">
                <div class="text-subtitle1">{{ invite.company.name }}</div>
                <div class="text-caption text-grey-7">{{ invite.role }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="row justify-between">
          <q-btn flat color="primary" label="Go Home" @click="router.push('/profile')" />
          <q-btn unelevated color="primary" label="Accept & Join" @click="respondToInvitation(true)" />
        </div>
      </div>

      <div v-else-if="!loading" class="text-center">
        <div class="q-mb-xl">
          <q-icon class="text-grey-4" name="mail_outline" size="120px" />
        </div>
        <div class="text-h5 q-mb-md">No pending invites</div>
        <div class="text-grey-7 q-mb-xl">
          You can see here if someone invites you to a workspace.
        </div>
        <q-btn flat color="primary" label="Back to home" @click="router.push('/profile')" />
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center">
        <q-spinner color="primary" size="2em" />
        <div class="text-subtitle1 q-mt-sm">Loading invitations...</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.onboarding-background {
  background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
  position: relative;
  overflow: hidden;
  min-height: 100vh;
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

.workspace-list {
  max-width: 500px;
  margin: 0 auto;
}

.workspace-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}

.company-avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--q-primary) 0%, #4F46E5 100%);
  color: white;
  font-size: 18px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 600px) {
  .onboarding-container {
    width: 95%;
    padding: 16px !important;
  }
}
</style>
