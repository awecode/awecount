<template>
  <div class="q-pa-md">
    <div class="row justify-end q-mb-md gap-4">
      <q-btn icon="settings" title="Config">
        <q-badge
          v-if="Object.values(config).filter(Boolean).length"
          floating
          color="primary"
          class="q-p-md"
          style="top: -10px; right: -10px; padding: 6px 8px"
        >
          {{ Object.values(config).filter(Boolean).length }}
        </q-badge>
        <q-menu>
          <div class="menu-wrapper" style="width: min(300px, 90vw)">
            <div style="border-bottom: 1px solid lightgrey">
              <h6 class="q-ma-md text-grey-9">Config</h6>
            </div>
            <div class="q-ma-sm">
              <div class="q-pb-sm">
                <q-checkbox
                  v-model="config.hide_accounts"
                  label="Hide Accounts?"
                ></q-checkbox>
              </div>
              <div class="q-pb-sm">
                <q-checkbox
                  v-model="config.hide_categories"
                  label="Hide Categories?"
                ></q-checkbox>
              </div>
              <div class="q-pb-sm">
                <q-checkbox
                  v-model="config.hide_zero_transactions"
                  label="Hide accounts/categories without transactions?"
                ></q-checkbox>
              </div>
            </div>
          </div>
        </q-menu>
      </q-btn>
      <q-btn
        v-if="checkPermissions('AccountCreate')"
        color="green"
        label="Add Account"
        class="add-btn"
        icon-right="add"
        @click="addAccountModalOpen = true"
      />

      <q-btn
        v-if="checkPermissions('CategoryCreate')"
        color="green"
        label="Add Category"
        icon-right="add"
        @click="addCategoryModalOpen = true"
      />
    </div>

    <q-markup-table>
      <q-table
        :columns="columns"
        virual-scroll
        :virtual-scroll-item-size="50"
        class="w-full"
        :rows="chartOfAccounts"
        :hide-pagination="true"
        :rows-per-page-options="[0]"
      >
        <template v-slot:body="props">
          <COATableNode
            v-if="
              props.row.id === 0 ||
              !(
                config.hide_zero_transactions &&
                props.row.total_transactions === 0
              )
            "
            :row="props.row"
            @drag-event="handleDragEvent"
            @edit-row="editRow"
            @add-category="handleAddCategoryEmitEvent"
            @add-account="handleAddAccountEmitEvent"
            v-model:currentTarget="currentTarget"
            v-model:draggingItem="draggingItem"
            :droppable-categories="droppableCategories"
            :config="config"
            root
          />
        </template>
      </q-table>
    </q-markup-table>

    <q-dialog v-model="dragDropConfirmDialog" class="overflow-visible">
      <q-card style="min-width: min(40vw, 500px)" class="overflow-visible">
        <q-card-section class="bg-primary text-white flex justify-between">
          <div class="text-h6 text-white">
            <span>Are you sure?</span>
          </div>
          <q-btn
            icon="close"
            class="text-red-700 bg-slate-200 opacity-95"
            flat
            round
            dense
            v-close-popup
          />
        </q-card-section>

        <q-card-section>
          <div class="text-subtitle1">
            {{ dragDropConfirmationMessage }}
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
          <q-btn flat label="Confirm" color="primary" @click="confirmAction" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="addCategoryModalOpen" transition-hide="none">
      <q-card style="min-width: 80vw">
        <CategoryForm
          :is-modal="true"
          @modalSignal="onCategoryAdd"
          :edit-id="categoryUpdateId"
          @closeModal="closeAccountModal()"
          :default-fields="addCategoryDefaults"
        />
      </q-card>
    </q-dialog>

    <q-dialog v-model="addAccountModalOpen" transition-hide="none">
      <q-card style="min-width: 80vw">
        <AccountForm
          :is-modal="true"
          @modalSignal="onAccountAdd"
          :edit-id="accountUpdateId"
          @closeModal="closeAccountModal()"
          :default-fields="addAccountDefaults"
        />
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import checkPermissions from 'src/composables/checkPermissions'
import CategoryForm from '../account/category/CategoryForm.vue'
import AccountForm from 'src/pages/account/ledger/LedgerForm.vue'

interface Account {
  id: number
  name: string
  code: string
  system_code: string | null
  category_id: number
  total_transactions: number
}

interface CategoryTree {
  id: number
  name: string
  children: CategoryTree[]
  code: string | null
  system_code: string | null
  tree_id: number
  rght: number
  lft: number
  default?: boolean
  total_transactions?: number
  accounts?: Account[]
  level?: number
  isExpandable?: boolean
  parent_id?: number
}

type DragItem =
  | {
      type: 'category'
      row: CategoryTree
    }
  | {
      type: 'account'
      row: Account
    }

type Config = {
  hide_accounts: boolean
  hide_categories: boolean
  hide_zero_transactions: boolean
}

const route = useRoute()
const router = useRouter()

const config = ref<Config>({
  hide_accounts: route.query.hide_accounts === 'true',
  hide_categories: route.query.hide_categories === 'true',
  hide_zero_transactions: route.query.hide_zero_transactions === 'true',
})

watchEffect(() => {
  const newQuery = {
    ...route.query,
    hide_accounts: config.value.hide_accounts === true ? 'true' : undefined,
    hide_categories: config.value.hide_categories === true ? 'true' : undefined,
    hide_zero_transactions:
      config.value.hide_zero_transactions === true ? 'true' : undefined,
  }
  router.replace({ query: newQuery })
})

useMeta({
  title: 'Chart of Accounts | Awecount',
})

const columns = [
  {
    name: 'name',
    required: true,
    label: 'Name',
    align: 'left',
    field: 'name',
    sortable: true,
  },
  {
    name: 'code',
    required: true,
    label: 'Code',
    align: 'left',
    field: 'code',
    sortable: true,
  },
  {
    name: 'system_code',
    required: true,
    label: 'System Code',
    align: 'left',
    field: 'system_code',
    sortable: true,
  },
  {
    name: 'total_transactions',
    required: true,
    label: 'Total Transactions',
    align: 'left',
    field: 'total_transactions',
    sortable: true,
  },
  {
    name: 'actions',
    required: true,
    label: '',
    align: 'left',
    field: 'actions',
    sortable: false,
  },
]

const dragDropConfirmDialog = ref(false)
const dragDropConfirmationMessage = ref('')
const dragDropUpdateItemId = ref<number | null>(null)
const dragDropUpdateType = ref<'category' | 'account' | null>(null)
const dragDropTargetCategoryId = ref<number | null>(null)

function confirmAction() {
  const apiEndpoint =
    dragDropUpdateType.value === 'category'
      ? `/v1/categories/${dragDropUpdateItemId.value}/`
      : `/v1/accounts/${dragDropUpdateItemId.value}/`

  const data =
    dragDropUpdateType.value === 'category'
      ? { parent: dragDropTargetCategoryId.value }
      : { category: dragDropTargetCategoryId.value }

  useApi(apiEndpoint, {
    method: 'PATCH',
    body: data,
  })
    .then(() => {
      if (dragDropUpdateType.value === 'category') {
        fetchCategoryTree()
      } else {
        fetchAccounts()
      }

      dragDropConfirmDialog.value = false
      dragDropConfirmationMessage.value = ''
      dragDropUpdateItemId.value = null
      dragDropUpdateType.value = null
      dragDropTargetCategoryId.value = null
    })
    .catch((err) => {
      console.log(err)
    })
}

const draggingItem = ref<DragItem | null>()

const currentTarget = ref<CategoryTree | null>()

const accounts = ref<Account[]>([])
const categoryTree = ref<CategoryTree[]>([])

function fetchAccounts() {
  useApi('/v1/chart-of-accounts/')
    .then((data) => {
      accounts.value = data
    })
    .catch((err) => {
      console.log(err)
    })
}

fetchAccounts()

function fetchCategoryTree() {
  useApi('/v1/category-tree/?include-empty=true', { method: 'GET' })
    .then((data) => {
      categoryTree.value = data
    })
    .catch((error) => {
      console.log('err fetching data', error)
    })
}

fetchCategoryTree()

const chartOfAccounts = computed(() => {
  const categoryAccountsMap: Record<number, Account[]> = {}
  accounts.value.forEach((account) => {
    if (!categoryAccountsMap[account.category_id]) {
      categoryAccountsMap[account.category_id] = []
    }
    categoryAccountsMap[account.category_id].push(account)
  })

  const calculateTransactions = (
    category: CategoryTree,
    level: number,
    parent_id?: number
  ): number => {
    let totalTransactions = 0

    if (categoryAccountsMap[category.id]) {
      totalTransactions += categoryAccountsMap[category.id].reduce(
        (sum, account) => sum + account.total_transactions,
        0
      )
      category.accounts = categoryAccountsMap[category.id]
    } else {
      category.accounts = []
    }

    if (category.children && category.children.length > 0) {
      category.children.forEach((child) => {
        totalTransactions += calculateTransactions(
          child,
          level + 1,
          category.id
        )
      })
    }

    category.total_transactions = totalTransactions
    category.level = level
    category.isExpandable =
      (category.children && category.children.length > 0) ||
      (!config.value.hide_accounts && category.accounts.length > 0)
    category.parent_id = parent_id
    return totalTransactions
  }

  const categoriesCopy = JSON.parse(JSON.stringify(categoryTree.value))
  categoriesCopy.unshift({
    id: 0,
    name: 'N/A',
    children: [],
    code: null,
    system_code: null,
    tree_id: 0,
    total_transactions: 0,
  })
  categoriesCopy.forEach((category: CategoryTree) => {
    calculateTransactions(category, 0, category.id)
  })

  return categoriesCopy
})

const handleDragEvent = ({
  source,
  target,
}: {
  source: { type: 'category' | 'account'; id: number }
  target: number | null
}) => {
  if (source.type === 'category') {
    const sourceRow = findRowById(chartOfAccounts.value, source.id)!
    const targetRow = target ? findRowById(chartOfAccounts.value, target) : null

    if (targetRow && sourceRow.id === targetRow.id) {
      return
    }

    dragDropConfirmationMessage.value = targetRow
      ? `Set category '${targetRow.name}' as parent of category '${sourceRow.name}'?`
      : `Set category '${sourceRow.name}' as root category?`
  } else {
    const account = findAccountById(chartOfAccounts.value, source.id)
    const targetRow = findRowById(chartOfAccounts.value, target!)

    if (account && targetRow) {
      if (account.category_id === targetRow.id) {
        return
      }

      dragDropConfirmationMessage.value = `Set category '${targetRow.name}' to account '${account.name}'?`
    }
  }
  dragDropConfirmDialog.value = true
  dragDropUpdateItemId.value = source.id
  dragDropUpdateType.value = source.type
  dragDropTargetCategoryId.value = target
}

const findRowById = (rows: CategoryTree[], id: number): CategoryTree | null => {
  for (const row of rows) {
    if (row.id === id) return row
    const childRow = findRowById(row.children || [], id)
    if (childRow) return childRow
  }
  return null
}

const findAccountById = (rows: CategoryTree[], id: number): Account | null => {
  for (const row of rows) {
    if (row.accounts) {
      const account = row.accounts.find((account) => account.id === id)
      if (account) return account
    }
    const childAccount = findAccountById(row.children || [], id)
    if (childAccount) return childAccount
  }
  return null
}

const canBeDropped = function (targetRow: CategoryTree) {
  const { type: draggingType, row: draggingRow } = draggingItem.value

  if (draggingType === 'category') {
    if (
      targetRow.tree_id === draggingRow.tree_id &&
      targetRow.rght < draggingRow.rght &&
      targetRow.lft > draggingRow.lft &&
      targetRow.level! > draggingRow.level!
    ) {
      return false
    }
    if (targetRow.id === draggingRow.parent_id || draggingRow.id === 0) {
      return false
    }
  } else if (draggingType === 'account') {
    if (targetRow.id === draggingRow.category_id) {
      return false
    }
  }

  if (
    (draggingType === 'account' ||
      draggingRow.level === 0 ||
      !draggingRow.default) &&
    targetRow.id === 0
  ) {
    return false
  }

  const sourceId =
    draggingType === 'category' ? draggingRow.id : draggingRow.category_id
  return sourceId !== targetRow.id
}

const droppableCategories = computed(() => {
  if (!draggingItem.value) return []

  const { type: draggingType, row: draggingRow } = draggingItem.value

  if (
    (draggingType === 'category' && !checkPermissions('CategoryModify')) ||
    (draggingType === 'account' && !checkPermissions('AccountModify'))
  ) {
    return []
  }

  const categoryIds = []

  const getDroppableCategoryIds = (rows) => {
    for (const row of rows) {
      if (canBeDropped(row)) {
        categoryIds.push(row.id)
      }
      if (row.children && row.children.length > 0) {
        getDroppableCategoryIds(row.children)
      }
    }
  }

  getDroppableCategoryIds(chartOfAccounts.value)
  return categoryIds
})

const addCategoryModalOpen = ref(false)
const categoryUpdateId = ref<number | null>(null)
const addCategoryDefaults = ref({})
function onCategoryAdd() {
  fetchCategoryTree()
  closeCategoryModal()
}

function closeCategoryModal() {
  addCategoryModalOpen.value = false
  categoryUpdateId.value = null
}

const addAccountModalOpen = ref(false)
const accountUpdateId = ref<number | null>(null)
const addAccountDefaults = ref({})
function onAccountAdd() {
  fetchAccounts()
  closeAccountModal()
}

function closeAccountModal() {
  addAccountModalOpen.value = false
  accountUpdateId.value = null
}

function editRow(type: 'category' | 'account', id: number) {
  if (type === 'category') {
    categoryUpdateId.value = id
    addCategoryModalOpen.value = true
  } else {
    accountUpdateId.value = id
    addAccountModalOpen.value = true
  }
}

function handleAddCategoryEmitEvent(id: number) {
  addCategoryModalOpen.value = true
  addCategoryDefaults.value = { parent: id }
}

function handleAddAccountEmitEvent(id: number) {
  addAccountModalOpen.value = true
  addAccountDefaults.value = { category: id }
}
</script>
