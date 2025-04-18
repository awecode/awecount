<script setup lang="ts">
import { useQuasar } from 'quasar'
import { $api } from '@/composables/api'
import { titelize } from '@/utils/string'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const $q = useQuasar()
const route = useRoute()

interface Permission {
  id: string
  name: string
  permissions: Record<string, Record<string, boolean>>
  created_at: string
}

interface Pagination {
  page: number
  page_size: number
  total: number
}

const permissions = ref<{ results: Permission[], pagination: Pagination }>({ results: [], pagination: { page: 1, page_size: 10, total: 0 } })
const defaultPermissions = ref<Record<string, Record<string, boolean>>>({})
const loading = ref(false)

// Form state
const showCreateDialog = ref(false)
const editingPermission = ref<Permission | null>(null)
const formState = reactive({
  name: '',
  permissions: {} as Record<string, Record<string, boolean>>,
})

// Add these module category definitions
const MODULE_CATEGORIES = {
  company: {
    order: 1,
    label: 'Company Management',
    modules: [
      'permission',
      'company_member',
      'company_member_invite',
      'api_key',
    ],
  },
  accounting: {
    order: 2,
    label: 'Accounting & Finance',
    modules: [
      'account',
      'journal_entry',
      'transaction',
      'transaction_charge',
      'account_opening_balance',
      'account_closing',
      'journal_voucher',
      'journal_voucher_row',
      'payment_receipt',
      'payment_mode',
    ],
  },
  party: {
    order: 3,
    label: 'Party Management',
    modules: [
      'party',
      'party_representative',
      'sales_agent',
    ],
  },
  inventory: {
    order: 4,
    label: 'Inventory Management',
    modules: [
      'unit',
      'brand',
      'inventory_account',
      'item',
      'inventory_setting',
      'bill_of_material',
      'bill_of_material_row',
      'inventory_adjustment_voucher',
      'inventory_adjustment_voucher_row',
      'inventory_conversion_voucher',
      'inventory_conversion_voucher_row',
      'transatcion_removal_log',
    ],
  },
  sales: {
    order: 5,
    label: 'Sales Management',
    modules: [
      'sales_voucher',
      'sales_voucher_row',
      'sales_discount',
      'sales_setting',
      'challan',
      'challan_row',
      'credit_note',
      'credit_note_row',
      'invoice_design',
      'recurring_voucher_template',
    ],
  },
  purchase: {
    order: 6,
    label: 'Purchase Management',
    modules: [
      'purchase_order',
      'purchase_order_row',
      'purchase_voucher',
      'purchase_voucher_row',
      'purchase_discount',
      'purchase_setting',
      'debit_note',
      'debit_note_row',
    ],
  },
  tax: {
    order: 7,
    label: 'Tax Management',
    modules: [
      'tax_scheme',
      'tax_payment',
    ],
  },
  import: {
    order: 8,
    label: 'Import/Export',
    modules: ['import'],
  },
} as const

// Add these computed helpers
const getModuleCheckedState = (moduleName: string) => {
  const modulePerms = formState.permissions[moduleName]
  if (!modulePerms) return false

  const values = Object.values(modulePerms)
  if (values.length === 0) return false

  if (values.every(v => v === true)) return true

  if (values.includes(true)) return null // Indeterminate if any are true

  return false
}

// Add this method to toggle all permissions for a module
const toggleModulePermissions = (moduleName: string, value: boolean) => {
  if (!formState.permissions[moduleName]) {
    formState.permissions[moduleName] = {}
  }

  const modulePerms = formState.permissions[moduleName]
  Object.keys(defaultPermissions.value[moduleName]).forEach((action) => {
    modulePerms[action] = value
  })
}

// Load permissions and defaults
const loadData = async () => {
  loading.value = true
  try {
    const [permsData, defaultsData] = await Promise.all([
      $api(`/api/company/${route.params.company}/permissions/`),
      $api(`/api/company/${route.params.company}/permissions/defaults/`),
    ])
    permissions.value = permsData
    defaultPermissions.value = defaultsData
  } catch (err) {
    console.error('Failed to load permissions:', err)
    $q.notify({
      type: 'negative',
      message: 'Failed to load permissions',
    })
  } finally {
    loading.value = false
  }
}

// Create/Update permission
const savePermission = async () => {
  try {
    if (editingPermission.value) {
      await $api(`/api/company/${route.params.company}/permissions/${editingPermission.value.id}/`, {
        method: 'PUT',
        body: formState,
      })
    } else {
      await $api(`/api/company/${route.params.company}/permissions/`, {
        method: 'POST',
        body: formState,
      })
    }

    showCreateDialog.value = false
    editingPermission.value = null
    formState.name = ''
    formState.permissions = {}
    await loadData()

    $q.notify({
      type: 'positive',
      message: `Permission ${editingPermission.value ? 'updated' : 'created'} successfully`,
    })
  } catch {
    $q.notify({
      type: 'negative',
      message: `Failed to ${editingPermission.value ? 'update' : 'create'} permission`,
    })
  }
}

// Delete permission
const deletePermission = async (id: string) => {
  try {
    await $api(`/api/company/${route.params.company}/permissions/${id}/`, {
      method: 'DELETE',
    })
    await loadData()

    $q.notify({
      type: 'positive',
      message: 'Permission deleted successfully',
    })
  } catch {
    $q.notify({
      type: 'negative',
      message: 'Failed to delete permission',
    })
  }
}

// Edit permission
const editPermission = (permission: Permission) => {
  editingPermission.value = permission
  formState.name = permission.name
  formState.permissions = JSON.parse(JSON.stringify(permission.permissions))
  showCreateDialog.value = true
}

// Create new permission
const createPermission = () => {
  editingPermission.value = null
  formState.name = ''
  formState.permissions = JSON.parse(JSON.stringify(defaultPermissions.value))
  showCreateDialog.value = true
}

const formatDate = (date: string) => {
  return Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date))
}

// Add a helper function to get all module names from defaultPermissions
const uncategorizedModules = computed(() => {
  // Get all module names from defaultPermissions
  const allModules = Object.keys(defaultPermissions.value)

  // Get all categorized modules
  const categorizedModules = Object.values(MODULE_CATEGORIES).flatMap(category => category.modules) as string[]

  // Return modules that aren't in any category
  return allModules.filter(module => !categorizedModules.includes(module))
})

onMounted(loadData)
</script>

<template>
  <div>
    <div class="row items-center justify-between q-mb-lg">
      <div class="text-h6">
        Permissions
      </div>
      <q-btn color="primary" label="Create Permission" @click="createPermission" />
    </div>

    <!-- Permissions List -->
    <q-table
      row-key="id"
      :columns="[
        { align: 'left', name: 'name', label: 'Name', field: 'name' },
        { align: 'left', name: 'created_at', label: 'Created', field: 'created_at' },
        { align: 'left', name: 'actions', label: 'Actions', field: 'actions' },
      ]"
      :loading="loading"
      :pagination="permissions.pagination"
      :rows="permissions.results"
      :rows-per-page-options="[]"
    >
      <template #body-cell-created_at="props">
        <q-td :props="props">
          {{ formatDate(props.row.created_at) }}
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            flat
            round
            color="primary"
            icon="edit"
            @click="editPermission(props.row)"
          >
            <q-tooltip>Edit Permission</q-tooltip>
          </q-btn>
          <q-btn
            flat
            round
            color="negative"
            icon="delete"
            @click="deletePermission(props.row.id)"
          >
            <q-tooltip>Delete Permission</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>

    <!-- Create/Edit Dialog -->
    <q-dialog v-model="showCreateDialog" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <div class="text-h6">
            {{ editingPermission ? 'Edit' : 'Create' }} Permission
          </div>
          <q-space />
          <q-btn
            v-close-popup
            flat
            round
            icon="close"
          />
        </q-card-section>

        <q-card-section class="q-pa-lg">
          <div class="row q-col-gutter-lg">
            <div class="col-12">
              <q-input
                v-model="formState.name"
                dense
                outlined
                label="Permission Name"
              />
            </div>

            <!-- Module Permissions -->
            <div class="col-12">
              <div class="text-subtitle1 q-mb-md">
                Module Permissions
              </div>
              <q-list
                bordered
                separator
                :style="{ maxHeight: '500px', width: '100%', overflowY: 'auto' }"
              >
                <template v-for="category in MODULE_CATEGORIES" :key="category">
                  <q-item-label header class="text-weight-bold bg-grey-2 q-pa-sm">
                    {{ category.label }}
                  </q-item-label>

                  <q-expansion-item
                    v-for="module in category.modules"
                    :key="module"
                    dense-toggle
                    class="bg-grey-1"
                  >
                    <template #header>
                      <q-item-section avatar>
                        <q-checkbox
                          :model-value="getModuleCheckedState(module)"
                          @update:model-value="toggleModulePermissions(module, $event)"
                        />
                      </q-item-section>

                      <q-item-section>
                        {{ titelize(module) }}
                      </q-item-section>
                    </template>

                    <q-card>
                      <q-card-section>
                        <div class="row q-col-gutter-sm">
                          <div v-for="(action, key) in defaultPermissions[module]" :key="key" class="col-12">
                            <q-checkbox
                              v-model="formState.permissions[module][key]"
                              :label="titelize(key)"
                            />
                          </div>
                        </div>
                      </q-card-section>
                    </q-card>
                  </q-expansion-item>
                </template>

                <q-item-label header class="text-weight-bold bg-grey-2 q-pa-sm">
                  Others
                </q-item-label>
                <q-expansion-item
                  v-for="module in uncategorizedModules"
                  :key="module"
                  dense-toggle
                  class="bg-grey-1"
                >
                  <template #header>
                    <q-item-section avatar>
                      <q-checkbox
                        :model-value="getModuleCheckedState(module)"
                        @update:model-value="toggleModulePermissions(module, $event)"
                      />
                    </q-item-section>

                    <q-item-section>
                      {{ titelize(module) }}
                    </q-item-section>
                  </template>

                  <q-card>
                    <q-card-section>
                      <div class="row q-col-gutter-sm">
                        <div v-for="(action, key) in defaultPermissions[module]" :key="key" class="col-12">
                          <q-checkbox
                            v-model="formState.permissions[module][key]"
                            :label="titelize(key)"
                          />
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </q-expansion-item>
              </q-list>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn
            v-close-popup
            flat
            color="primary"
            label="Cancel"
          />
          <q-btn
            unelevated
            color="primary"
            :label="`${editingPermission ? 'Update' : 'Create'}`"
            @click="savePermission"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped>
.q-card {
  max-width: 100%;
}
</style>
