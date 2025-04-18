<script setup lang="ts">
import { useQuasar } from 'quasar'
import { useRoute } from 'vue-router'

const { $api } = useNuxtApp()

const $q = useQuasar()
const route = useRoute()

interface Member {
  id: string
  member: {
    email: string
    full_name: string
  }
  role: 'owner' | 'admin' | 'member'
  created_at: string
}

interface Invitation {
  id: string
  email: string
  role: 'admin' | 'member'
  created_at: string
}

interface Pagination {
  page: number
  page_size: number
  total: number
}

interface Permission {
  id: string
  name: string
  description: string
}

const members = ref<{ results: Member[], pagination: Pagination }>({ results: [], pagination: { page: 1, page_size: 10, total: 0 } })
const invitations = ref<{ results: Invitation[], pagination: Pagination }>({ results: [], pagination: { page: 1, page_size: 10, total: 0 } })
const loading = ref(false)

// New member form
const showInviteDialog = ref(false)
const newInvites = ref([
  { email: '', role: 'member', permissions: [] as string[] },
])

const roles = [
  { label: 'Member', value: 'member' },
  { label: 'Admin', value: 'admin' },
]

// Add permissions ref
const permissions = ref<Permission[]>([])

// Load members and invitations
const loadData = async () => {
  loading.value = true
  try {
    const [membersData, invitationsData] = await Promise.all([
      $api(`/api/company/${route.params.company}/members/`),
      $api(`/api/company/${route.params.company}/invitations/`),
    ])
    members.value = membersData
    invitations.value = invitationsData
  } catch (err) {
    console.error('Failed to load members data:', err)
    $q.notify({
      type: 'negative',
      message: 'Failed to load members data',
    })
  } finally {
    loading.value = false
  }
}

// Load permissions
const loadPermissions = async () => {
  try {
    const response = await $api(`/api/company/${route.params.company}/permissions/`)
    permissions.value = response
  } catch (err) {
    console.error('Failed to load permissions:', err)
    $q.notify({
      type: 'negative',
      message: 'Failed to load permissions',
    })
  }
}

// Add new invite field
const addInvite = () => {
  newInvites.value.push({ email: '', role: 'member', permissions: [] })
}

// Remove invite field
const removeInvite = (index: number) => {
  newInvites.value.splice(index, 1)
}

// Send invitations
const sendInvites = async () => {
  try {
    await $api(`/api/company/${route.params.company}/invitations/`, {
      method: 'POST',
      body: {
        emails: newInvites.value,
      },
    })

    $q.notify({
      type: 'positive',
      message: 'Invitations sent successfully',
    })

    showInviteDialog.value = false
    newInvites.value = [{ email: '', role: 'member', permissions: [] }]
    await loadData()
  } catch (err: any) {
    if (err.response?.data?.error) {
      $q.notify({
        type: 'negative',
        message: err.response.data.error,
      })
    } else {
      $q.notify({
        type: 'negative',
        message: 'Failed to send invitations',
      })
    }
  }
}

// Remove member
const removeMember = async (id: string) => {
  try {
    await $api(`/api/company/${route.params.company}/members/${id}/`, {
      method: 'DELETE',
    })
    await loadData()

    $q.notify({
      type: 'positive',
      message: 'Member removed successfully',
    })
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Failed to remove member',
    })
  }
}

// Cancel invitation
const cancelInvitation = async (id: string) => {
  try {
    await $api(`/api/company/${route.params.company}/invitations/${id}/`, {
      method: 'DELETE',
    })
    await loadData()

    $q.notify({
      type: 'positive',
      message: 'Invitation cancelled successfully',
    })
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Failed to cancel invitation',
    })
  }
}

const toggleInviteDialog = () => {
  showInviteDialog.value = !showInviteDialog.value

  if (showInviteDialog.value) {
    loadPermissions()
  }
}

const formatDate = (date: string) => {
  return Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date))
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div>
    <div class="row items-center justify-between q-mb-lg">
      <div class="text-h6">
        Members
      </div>
      <q-btn color="primary" label="Invite Members" @click="toggleInviteDialog" />
    </div>

    <!-- Members List -->
    <div class="text-subtitle2 q-mb-sm">
      Members
    </div>
    <q-table
      row-key="id"
      :columns="[
        { align: 'left', name: 'member', label: 'Member', field: row => row.member.full_name || row.member.email },
        { align: 'left', name: 'email', label: 'Email', field: row => row.member.email },
        { align: 'left', name: 'role', label: 'Role', field: 'role' },
        { align: 'left', name: 'permission', label: 'Permissions', field: 'permissions' },
        { align: 'left', name: 'joined', label: 'Joined', field: 'created_at' },
        { align: 'left', name: 'actions', label: 'Actions', field: 'actions' },
      ]"
      :loading="loading"
      :pagination="members.pagination"
      :rows="members.results"
      :rows-per-page-options="[]"
    >
      <template #body-cell-role="props">
        <q-td class="text-capitalize" :props="props">
          {{ props.value }}
        </q-td>
      </template>
      <template #body-cell-joined="props">
        <q-td :props="props">
          {{ formatDate(props.row.created_at) }}
        </q-td>
      </template>
      <template #body-cell-permission="props">
        <q-td :props="props" :style="{ maxWidth: '200px', display: 'flex', flexWrap: 'wrap', gap: '4px' }">
          <template v-if="['owner', 'admin'].includes(props.row.role)">
            <q-chip label="Full Access" />
          </template>
          <template v-else>
            <q-chip v-for="perm in props.row.permissions" :key="perm" :label="perm.name" />
          </template>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="props.row.role !== 'owner'"
            flat
            round
            color="negative"
            icon="person_remove"
            @click="removeMember(props.row.id)"
          >
            <q-tooltip>Remove Member</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>

    <!-- Pending Invitations -->
    <div class="text-subtitle2 q-mt-lg q-mb-sm">
      Pending Invitations
    </div>
    <q-table
      row-key="id"
      :columns="[
        { align: 'left', name: 'email', label: 'Email', field: 'email' },
        { align: 'left', name: 'role', label: 'Role', field: 'role' },
        { align: 'left', name: 'permission', label: 'Permissions', field: 'permissions' },
        { align: 'left', name: 'sent', label: 'Sent', field: 'created_at' },
        { align: 'left', name: 'actions', label: 'Actions', field: 'actions' },
      ]"
      :loading="loading"
      :pagination="invitations.pagination"
      :rows="invitations.results"
      :rows-per-page-options="[]"
    >
      <template #body-cell-role="props">
        <q-td class="text-capitalize" :props="props">
          {{ props.value }}
        </q-td>
      </template>

      <template #body-cell-permission="props">
        <q-td :props="props" :style="{ maxWidth: '200px', display: 'flex', flexWrap: 'wrap', gap: '4px' }">
          <template v-if="['owner', 'admin'].includes(props.row.role)">
            <q-chip label="Full Access" />
          </template>
          <template v-else>
            <q-chip v-for="perm in props.row.permissions" :key="perm" :label="perm.name" />
          </template>
        </q-td>
      </template>

      <template #body-cell-sent="props">
        <q-td :props="props">
          {{ formatDate(props.row.created_at) }}
        </q-td>
      </template>

      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            flat
            round
            color="negative"
            icon="delete"
            @click="cancelInvitation(props.row.id)"
          >
            <q-tooltip>Cancel Invitation</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>

    <!-- Invite Dialog -->
    <q-dialog v-model="showInviteDialog">
      <q-card style="min-width: 650px">
        <q-card-section>
          <div class="text-h6">
            Invite Members
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div v-for="(invite, index) in newInvites" :key="index" class="q-mb-md">
            <div class="row q-col-gutter-sm items-center">
              <div class="col">
                <q-input
                  v-model="invite.email"
                  dense
                  outlined
                  label="Email"
                  type="email"
                />
              </div>
              <div class="col-4">
                <q-select
                  v-model="invite.role"
                  dense
                  emit-value
                  map-options
                  outlined
                  label="Role"
                  :options="roles"
                />
              </div>
              <div class="col-auto">
                <q-btn
                  v-if="index > 0"
                  flat
                  round
                  color="negative"
                  icon="remove"
                  @click="removeInvite(index)"
                >
                  <q-tooltip>Remove</q-tooltip>
                </q-btn>
              </div>
            </div>

            <!-- Add permissions selection for member role -->
            <!-- <div v-if="invite.role === 'member'" class="q-mt-sm">
              <div class="text-caption q-mb-xs">
                Permissions
              </div>
              <q-option-group
                v-model="invite.permissions"
                type="checkbox"
                :options="permissions.map(p => ({
                  label: p.name,
                  value: p.id,
                }))"
              >
                <template #default="{ option }">
                  <div class="q-mb-sm">
                    <q-checkbox
                      v-model="invite.permissions"
                      :label="option.label"
                      :val="option.value"
                    />
                    <div class="text-caption text-grey-7 q-ml-lg">
                      {{ permissions.find(p => p.id === option.value)?.description }}
                    </div>
                  </div>
                </template>
              </q-option-group>
            </div> -->
            <!-- <div v-else class="q-mt-sm text-caption text-grey-7">
              {{ invite.role === 'admin' ? 'Full access to all features' : '' }}
            </div> -->
          </div>

          <div class="row justify-center q-mt-md">
            <q-btn
              flat
              color="primary"
              icon="add"
              label="Add Another"
              @click="addInvite"
            />
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
            unelevated
            color="primary"
            label="Send Invites"
            @click="sendInvites"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>
