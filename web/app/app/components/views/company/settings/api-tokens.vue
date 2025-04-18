<script setup lang="ts">
import { useQuasar } from 'quasar'
import { useRoute } from 'vue-router'

const { $api } = useNuxtApp()

const $q = useQuasar()
const route = useRoute()

interface APIKey {
  id: string
  name: string
  prefix: string
  created_at: string
  expiry_date: string
}

interface Pagination {
  count: number
  next: string | null
  previous: string | null
}

const data = ref<{ results: APIKey[], pagination: Pagination }>(
  {
    results: [],
    pagination: {
      count: 0,
      next: null,
      previous: null,
    },
  },
)

const loading = ref(false)

// New token form
const newToken = reactive({
  name: '',
  expiry_date: null,
})

const showCreateDialog = ref(false)
const showKeyDialog = ref(false)
const newlyCreatedKey = ref('')

// Load tokens
const loadTokens = async () => {
  loading.value = true
  try {
    data.value = await $api(`/api/company/${route.params.company}/api-tokens/`)
  } catch (err) {
    console.error('Failed to load API tokens:', err)
    $q.notify({
      type: 'negative',
      message: 'Failed to load API tokens',
    })
  } finally {
    loading.value = false
  }
}

// Create token
const createToken = async () => {
  try {
    const data = await $api(`/api/company/${route.params.company}/api-tokens/`, {
      method: 'POST',
      body: newToken,
    })

    // Show the key to user
    newlyCreatedKey.value = data.key
    showKeyDialog.value = true
    showCreateDialog.value = false

    // Reset form
    newToken.name = ''
    newToken.expiry_date = null

    // Reload tokens
    await loadTokens()
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Failed to create API token',
    })
  }
}

// Revoke token
const revokeToken = async (id: string) => {
  try {
    await $api(`/api/company/${route.params.company}/api-tokens/${id}/`, {
      method: 'DELETE',
    })
    await loadTokens()

    $q.notify({
      type: 'positive',
      message: 'API token revoked successfully',
    })
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Failed to revoke API token',
    })
  }
}

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
  $q.notify({
    type: 'positive',
    message: 'API token copied to clipboard',
  })
}

const formatDate = (date: string) => {
  return Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date))
}

onMounted(loadTokens)
</script>

<template>
  <div>
    <div class="row items-center justify-between q-mb-lg">
      <div class="text-h6">
        API Tokens
      </div>
      <q-btn color="primary" label="Create Token" @click="showCreateDialog = true" />
    </div>

    <!-- Tokens List -->
    <q-table
      row-key="id"
      :columns="[
        { align: 'left', name: 'name', label: 'Name', field: 'name' },
        { align: 'left', name: 'prefix', label: 'Prefix', field: 'prefix' },
        { align: 'left', name: 'created_at', label: 'Created', field: 'created_at' },
        { align: 'left', name: 'expiry_date', label: 'Expires', field: 'expiry_date' },
        { align: 'left', name: 'actions', label: 'Actions', field: 'actions' },
      ]"
      :loading="loading"
      :pagination="data.pagination"
      :rows="data.results"
      :rows-per-page-options="[]"
    >
      <template #body-cell-created_at="props">
        <q-td :props="props">
          {{ formatDate(props.row.created_at) }}
        </q-td>
      </template>
      <template #body-cell-expiry_date="props">
        <q-td :props="props">
          {{ formatDate(props.row.expiry_date) }}
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            flat
            round
            color="negative"
            icon="delete"
            @click="revokeToken(props.row.id)"
          >
            <q-tooltip>Revoke Token</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>

    <!-- Create Dialog -->
    <q-dialog v-model="showCreateDialog">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">
            Create API Token
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="newToken.name"
            dense
            outlined
            label="Token Name"
          />
          <q-input
            v-model="newToken.expiry_date"
            dense
            outlined
            class="q-mt-sm"
            label="Expiry Date"
            type="date"
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
            unelevated
            color="primary"
            label="Create"
            @click="createToken"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Show Key Dialog -->
    <q-dialog v-model="showKeyDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">
            API Token Created
          </div>
        </q-card-section>

        <q-card-section>
          <p class="text-subtitle2 q-mb-none">
            Please copy your API token now. You won't be able to see it again!
          </p>
          <q-input
            v-model="newlyCreatedKey"
            outlined
            readonly
            class="q-mt-sm"
          >
            <template #append>
              <q-btn
                flat
                round
                icon="content_copy"
                @click="copyToClipboard(newlyCreatedKey)"
              >
                <q-tooltip>Copy to clipboard</q-tooltip>
              </q-btn>
            </template>
          </q-input>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            v-close-popup
            flat
            color="primary"
            label="Close"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>
