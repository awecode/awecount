<template>
  <div class="q-pa-md">
    <div class="row justify-end q-mb-md gap-4">
      <q-btn
        v-if="checkPermissions('AccountCreate')"
        color="green"
        label="Add Account"
        class="add-btn"
        icon-right="add"
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
      <table class="w-full" style="border-collapse: collapse">
        <thead>
          <tr>
            <th colspan="4" class="text-left">Name</th>
            <th class="text-left">Code</th>
            <th class="text-left">System Code</th>
            <th class="text-left">Total Transactions</th>
          </tr>
        </thead>
        <tbody>
          <COATableNode
            v-for="row in chartOfAccounts"
            :key="row.id"
            :row="row"
            @drag-event="handleDragEvent"
            v-model:currentTarget="currentTarget"
            v-model:draggingItem="draggingItem"
            :can-be-dropped="canBeDropped"
            root
          />
        </tbody>
      </table>
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
          @closeModal="addCategoryModalOpen = false"
        />
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import checkPermissions from 'src/composables/checkPermissions'
import CategoryForm from '../account/category/CategoryForm.vue'

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

const currentTarget = ref<DragItem | null>()

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
  useApi('/v1/category-tree/', { method: 'GET' })
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
      category.accounts.length > 0
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

const canBeDropped = computed(() => {
  if (!draggingItem.value || !currentTarget.value) return false

  const { type: draggingType, row: draggingRow } = draggingItem.value
  const { type: targetType, row: targetRow } = currentTarget.value

  if (draggingType === 'category') {
    if (targetType === 'category') {
      if (
        targetRow.tree_id === draggingRow.tree_id &&
        targetRow.level! > draggingRow.level!
      )
        return false
      if (targetRow.id === draggingRow.parent_id) return false
    } else if (targetType === 'account') {
      return false
    }
  } else if (draggingType === 'account') {
    if (
      targetType === 'account' &&
      targetRow.category_id === draggingRow.category_id
    )
      return false
    if (targetType === 'category' && targetRow.id === draggingRow.category_id)
      return false
  }

  if (
    (draggingType === 'account' || draggingRow.level == 0) &&
    targetRow.id === 0
  )
    return false

  const sourceId =
    draggingType === 'category' ? draggingRow.id : draggingRow.category_id
  if (sourceId === targetRow.id) return false

  return true
})

const addCategoryModalOpen = ref(false)
function onCategoryAdd() {
  addCategoryModalOpen.value = false
  fetchCategoryTree()
}
</script>
