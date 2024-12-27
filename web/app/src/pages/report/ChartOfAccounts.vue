<template>
  <div class="q-pa-md">
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
            :root="true"
            :expandedRows="expandedRows"
            @toggle-expand="toggleExpand"
          />
        </tbody>
      </table>
    </q-markup-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

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
  total_transactions?: number
  accounts?: Account[]
  level?: number
  isExpandable?: boolean
}

const accounts = ref<Account[]>([])
const categoryTree = ref<CategoryTree[]>([])

useApi('/v1/chart-of-accounts/')
  .then((data) => {
    accounts.value = data
  })
  .catch((err) => {
    console.log(err)
  })

useApi('/v1/category-tree/', { method: 'GET' })
  .then((data) => {
    categoryTree.value = data
  })
  .catch((error) => {
    console.log('err fetching data', error)
  })

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
    level: number
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
        totalTransactions += calculateTransactions(child, level + 1)
      })
    }

    category.total_transactions = totalTransactions
    category.level = level
    category.isExpandable =
      (category.children && category.children.length > 0) ||
      category.accounts.length > 0
    return totalTransactions
  }

  const categoriesCopy = JSON.parse(JSON.stringify(categoryTree.value))
  categoriesCopy.forEach((category: CategoryTree) => {
    calculateTransactions(category, 0)
  })

  return categoriesCopy
})

const expandedRows = ref<Record<number, boolean>>({})

const toggleExpand = (id: number) => {
  expandedRows.value[id] = !expandedRows.value[id]
}
</script>
