<script setup lang="ts">
import DateConverter from 'src/components/date/VikramSamvat.js'
import AccountBalanceTableNode from 'src/components/report/AccountBalanceTableNode.vue'
import { useLoginStore } from 'src/stores/login-info'

interface Account {
  id: number
  name: string
  category_id: number
  cd: number | null
  cc: number | null
  transaction_data: {
    closing_dr: number
    closing_cr: number
  }[]
}

interface CategoryNode {
  id: number
  name?: string
  code?: string
  children: CategoryNode[]
  system_code?: string | null
  accounts?: Account[] // To hold the mapped accounts
  total: { closing_dr: number, closing_cr: number }[]
}

interface CategoryTree {
  [key: string]: CategoryNode[]
}
const route = useRoute()
const $q = useQuasar()
const router = useRouter()

const categoryTree = ref<CategoryTree | null>(null)

const store = useLoginStore()

const getLocalDate = (date: string | null) => {
  if (!date) {
    return ''
  }
  return DateConverter.getRepresentation(date, store.isCalendarInAD ? 'ad' : 'bs')
}

const config = ref({
  hide_accounts: true,
  hide_categories: false,
  hide_sums: false,
  show_opening_closing_dr_cr: false,
  hide_zero_balance: true,
})
const isLoading = ref(false)
const fields = ref<{
  start_date: string | null
  end_date: string | null
}>({
  start_date: null,
  end_date: null,
})

const column = ref({
  start_date: null as null | string,
  end_date: null as null | string,
})

const columns = ref<(typeof column.value)[]>([])

const extraData = ref({
  opening_stock: [] as number[],
  closing_stock: [] as number[],
})

// Fix for the new Array() linter error
const createTransactionData = (currentIndex: number) => {
  return Array.from({ length: currentIndex }, () => ({
    closing_dr: 0,
    closing_cr: 0,
  }))
}

const mapAccountsToCategories = (categories: CategoryNode[], accounts: Account[]) => {
  const categoryMap = new Map<number, Account[]>()

  // Group accounts by category_id
  for (const account of accounts) {
    account.transaction_data = [
      {
        closing_dr: account.cd || 0,
        closing_cr: account.cc || 0,
      },
    ]
    if (!categoryMap.has(account.category_id)) {
      categoryMap.set(account.category_id, [])
    }
    categoryMap.get(account.category_id)!.push(account)
  }

  const calculateTotalWithChildren = (node: CategoryNode): { closing_dr: number, closing_cr: number }[] => {
    // Get the totals for the current node's accounts
    const currentNodeTotal = categoryMap.get(node.id)?.reduce(
      (acc, account) => {
        account.transaction_data.forEach((data, index) => {
          if (!acc[index]) {
            acc[index] = { closing_dr: 0, closing_cr: 0 }
          }
          acc[index].closing_dr += data.closing_dr
          acc[index].closing_cr += data.closing_cr
        })
        return acc
      },
      [{ closing_dr: 0, closing_cr: 0 }],
    ) || [{ closing_dr: 0, closing_cr: 0 }]

    // Recursively calculate totals for all children
    const childrenTotal = node.children.reduce(
      (acc, child) => {
        const childTotal = calculateTotalWithChildren(child)
        childTotal.forEach((data, index) => {
          if (!acc[index]) {
            acc[index] = { closing_dr: 0, closing_cr: 0 }
          }
          acc[index].closing_dr += data.closing_dr
          acc[index].closing_cr += data.closing_cr
        })
        return acc
      },
      [{ closing_dr: 0, closing_cr: 0 }],
    )

    // Combine current node totals with children totals
    return currentNodeTotal.map((data, index) => ({
      closing_dr: data.closing_dr + (childrenTotal[index]?.closing_dr || 0),
      closing_cr: data.closing_cr + (childrenTotal[index]?.closing_cr || 0),
    }))
  }

  const addAccountsToTree = (nodes: CategoryNode[]) => {
    for (const node of nodes) {
      // Initialize accounts and totals if they don't exist
      node.accounts = categoryMap.get(node.id) || []
      node.total = calculateTotalWithChildren(node)

      // Recursively handle child nodes
      if (node.children.length > 0) {
        addAccountsToTree(node.children)
      }
    }
  }

  // Start processing the category tree
  addAccountsToTree(categories)
}

const countryIso = ref('')
const corporateTaxRate = ref(0)

const fetchData = () => {
  isLoading.value = true
  const endpoint = `/api/company/${route.params.company}/income-statement/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
  useApi(endpoint)
    .then((data) => {
      categoryTree.value = data.category_tree
      // Now loop in category_tree and map accounts to category in accounts array
      if (!categoryTree.value) {
        return
      }
      extraData.value.opening_stock = [data.opening_stock]
      extraData.value.closing_stock = [data.closing_stock]

      for (const categoryGroup of Object.values(categoryTree.value)) {
        mapAccountsToCategories(categoryGroup, data.accounts)
      }
      columns.value = [
        {
          start_date: fields.value.start_date,
          end_date: fields.value.end_date,
        },
      ]
      countryIso.value = data.country_iso
      corporateTaxRate.value = data.corporate_tax_rate
    })
    .catch(err => console.error(err))
    .finally(() => {
      isLoading.value = false
    })
}

const updateAccountsAndRecalculateTotals = (categories: CategoryNode[], newAccounts: Account[], currentIndex: number) => {
  const categoryMap = new Map<number, Account[]>()

  // Populate categoryMap with existing accounts
  const populateCategoryMap = (nodes: CategoryNode[]) => {
    for (const node of nodes) {
      if (!categoryMap.has(node.id)) {
        categoryMap.set(node.id, node.accounts || [])
      }
      if (node.children.length > 0) {
        populateCategoryMap(node.children)
      }
    }
  }
  populateCategoryMap(categories)

  // Update or add accounts in the categoryMap
  for (const [categoryId, accounts] of categoryMap.entries()) {
    const newAccountsForCategory = newAccounts.filter(newAccount => newAccount.category_id === categoryId)

    // Update existing accounts
    for (const account of accounts) {
      const matchingNewAccount = newAccountsForCategory.find(newAccount => newAccount.id === account.id)

      if (matchingNewAccount) {
        // Ensure transaction_data array has enough elements
        while (account.transaction_data.length <= currentIndex) {
          account.transaction_data.push({ closing_dr: 0, closing_cr: 0 })
        }
        account.transaction_data[currentIndex] = {
          closing_dr: matchingNewAccount.cd || 0,
          closing_cr: matchingNewAccount.cc || 0,
        }
      } else {
        // Add a placeholder for the current index if not in new data
        while (account.transaction_data.length <= currentIndex) {
          account.transaction_data.push({ closing_dr: 0, closing_cr: 0 })
        }
      }
    }

    // Add new accounts not already in the category
    for (const newAccount of newAccountsForCategory) {
      if (!accounts.some(account => account.id === newAccount.id)) {
        const newTransactionData = createTransactionData(currentIndex)
        newTransactionData[currentIndex] = {
          closing_dr: newAccount.cd || 0,
          closing_cr: newAccount.cc || 0,
        }

        newAccount.transaction_data = newTransactionData
        accounts.push(newAccount)
      }
    }
  }

  // Recursive function to calculate totals for the tree
  const calculateTotals = (node: CategoryNode): { closing_dr: number, closing_cr: number }[] => {
    const currentNodeAccounts = categoryMap.get(node.id) || []

    // Aggregate totals for the current node's accounts
    const currentNodeTotal = currentNodeAccounts.reduce((acc, account) => {
      account.transaction_data.forEach((data, index) => {
        if (!acc[index]) {
          acc[index] = { closing_dr: 0, closing_cr: 0 }
        }
        acc[index].closing_dr += data.closing_dr
        acc[index].closing_cr += data.closing_cr
      })
      return acc
    }, [] as { closing_dr: number, closing_cr: number }[])

    // Recursively aggregate totals for child nodes
    const childrenTotal = node.children.reduce((acc, child) => {
      const childTotal = calculateTotals(child)
      childTotal.forEach((data, index) => {
        if (!acc[index]) {
          acc[index] = { closing_dr: 0, closing_cr: 0 }
        }
        acc[index].closing_dr += data.closing_dr
        acc[index].closing_cr += data.closing_cr
      })
      return acc
    }, [] as { closing_dr: number, closing_cr: number }[])

    // Combine current node totals with children totals
    const maxLength = Math.max(currentNodeTotal.length, childrenTotal.length)
    const combinedTotal = Array.from({ length: maxLength }, (_, index) => ({
      closing_dr: (currentNodeTotal[index]?.closing_dr || 0) + (childrenTotal[index]?.closing_dr || 0),
      closing_cr: (currentNodeTotal[index]?.closing_cr || 0) + (childrenTotal[index]?.closing_cr || 0),
    }))
    return combinedTotal
  }

  // Update the tree with recalculated totals
  const updateTree = (nodes: CategoryNode[]) => {
    for (const node of nodes) {
      node.accounts = categoryMap.get(node.id) || []
      node.total = calculateTotals(node)
      // if the node total is an empty array, then set have it empty objects of the same length as the columns
      if (node.total.length === 0) {
        node.total = Array.from({ length: columns.value.length + 1 }, () => ({
          closing_dr: 0,
          closing_cr: 0,
        }))
      }

      // Recursively process child nodes
      if (node.children.length > 0) {
        updateTree(node.children)
      }
    }
  }
  updateTree(categories)
}

const addColumn = async () => {
  // Validate input dates
  if (!column.value.start_date || !column.value.end_date) {
    return
  }
  // Check if the column already exists
  if (columns.value.some(col => col.start_date === column.value.start_date && col.end_date === column.value.end_date)) {
    $q.notify({
      message: 'Column already exists',
      color: 'red',
      position: 'top',
    })
    return
  }

  isLoading.value = true

  const endpoint = `/api/company/${route.params.company}/income-statement/?start_date=${column.value.start_date}&end_date=${column.value.end_date}`

  try {
    const data = await useApi(endpoint) // Fetch data
    if (!categoryTree.value) {
      return
    }
    for (const categoryGroup of Object.values(categoryTree.value)) {
      updateAccountsAndRecalculateTotals(categoryGroup, data.accounts, columns.value.length)
    }
    extraData.value.opening_stock.push(data.opening_stock)
    extraData.value.closing_stock.push(data.closing_stock)

    // Add new column
    columns.value.push({
      start_date: column.value.start_date,
      end_date: column.value.end_date,
    })
  } catch (err) {
    console.error('Error fetching data:', err)
  } finally {
    isLoading.value = false
  }
}

// to replace link '/' with base url
const replaceHrefAttribute = (element, baseUrl) => {
  if (!element || !element.childNodes) return
  for (let i = 0; i < element.childNodes.length; i++) {
    const child = element.childNodes[i]
    if (child.tagName === 'A') {
      const link = child.getAttribute('href')
      child.setAttribute('href', `${baseUrl}${link}`)
    }
    replaceHrefAttribute(child, baseUrl)
  }
}

// Computed properties for calculations
const grossProfit = computed(() => {
  if (!categoryTree.value) return []

  return extraData.value.closing_stock.map((_, index) => {
    const purchase = categoryTree.value?.purchase?.[0]?.total[index] || { closing_dr: 0, closing_cr: 0 }
    const directExpense = categoryTree.value?.direct_expense?.[0]?.total[index] || { closing_dr: 0, closing_cr: 0 }
    const openingStock = extraData.value.opening_stock[index] || 0
    const closingStock = extraData.value.closing_stock[index] || 0

    return (purchase.closing_dr + directExpense.closing_dr
      - (purchase.closing_cr + directExpense.closing_cr)
      + openingStock - closingStock
      + directExpense.closing_dr)
    - directExpense.closing_cr
  })
})

const operatingProfit = computed(() => {
  if (!categoryTree.value) return []

  return grossProfit.value.map((gross, index) => {
    const otherIncome = categoryTree.value?.other_income?.[0]?.total[index] || { closing_dr: 0, closing_cr: 0 }
    const operatingExpense = categoryTree.value?.operating_expense?.[0]?.total[index] || { closing_dr: 0, closing_cr: 0 }

    return gross
      + (otherIncome.closing_dr - otherIncome.closing_cr)
      - (operatingExpense.closing_dr - operatingExpense.closing_cr)
  })
})

const earningsBeforeTaxes = computed(() => {
  if (!categoryTree.value) return []

  return operatingProfit.value.map((operating, index) => {
    const interestIncome = categoryTree.value?.interest_income?.[0]?.total[index] || { closing_dr: 0, closing_cr: 0 }
    const interestExpense = categoryTree.value?.interest_expense?.[0]?.total[index] || { closing_dr: 0, closing_cr: 0 }

    return operating
      + (interestIncome.closing_dr - interestIncome.closing_cr)
      - (interestExpense.closing_dr - interestExpense.closing_cr)
  })
})

const taxes = computed(() => {
  if (!categoryTree.value) return []

  return operatingProfit.value.map((operating) => {
    const taxRate = corporateTaxRate.value ? corporateTaxRate.value / 100 : 0.25
    return countryIso.value === 'NP' || corporateTaxRate.value ? operating * taxRate : 0
  })
})

const netIncome = computed(() => {
  return earningsBeforeTaxes.value.map((earnings, index) => {
    return earnings - taxes.value[index]
  })
})

// Fix for the Element.rows type error
const getTableCell = (element: Element, row: number, col: number): HTMLElement | null => {
  const table = element as HTMLTableElement
  return table.rows?.[row]?.cells?.[col] || null
}

const onDownloadXls = async () => {
  const XLSX = await import('xlsx-js-style')
  const elt = document.getElementById('tableRef') as HTMLTableElement
  if (!elt) return

  const baseUrl = window.location.origin
  replaceHrefAttribute(elt, baseUrl)

  const worksheet = XLSX.utils.table_to_sheet(elt)

  for (const i in worksheet) {
    if (typeof worksheet[i] != 'object') continue
    const cell = XLSX.utils.decode_cell(i)
    worksheet[i].s = {
      font: { name: 'Courier', sz: 12 },
    }

    if (cell.r === 0) {
      worksheet[i].s.font.bold = true
    }

    if (cell.c === 0) {
      const td = getTableCell(elt, cell.r, cell.c)
      if (td) {
        worksheet[i].s.font.italic = getComputedStyle(td).fontStyle === 'italic'
        const hexCode = getComputedStyle(td).color
        const hexArray = hexCode.slice(4, hexCode.length - 1).split(',')
        const numsArray = hexArray.map(e => Number(e))
        const rgbValue = ((1 << 24) | (numsArray[0] << 16) | (numsArray[1] << 8) | numsArray[2]).toString(16).slice(1)
        worksheet[i].s.font.color = { rgb: `${rgbValue}` }
      }
    }

    if (cell.r > -1) {
      const td = getTableCell(elt, cell.r, cell.c)
      if (td) {
        worksheet[i].s.font.bold = Number(getComputedStyle(td).fontWeight) >= 500
      }
    }
  }

  worksheet['!cols'] = Array.from({ length: 11 }).fill({ width: 16 })
  worksheet['!cols'][0] = { width: 50 }

  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Income Statement')
  XLSX.writeFileXLSX(workbook, 'IncomeStatement.xls')
}

function updateData() {
  const query = { ...fields.value }
  router.push({ path: `/${route.params.company}/reports/income-statement/`, query })
  fetchData()
}
if (route.query.start_date && route.query.end_date) {
  fields.value.start_date = route.query.start_date as string
  fields.value.end_date = route.query.end_date as string
  fetchData()
}

// Update the calculateCategoryTotals function to handle multiple columns
const calculateCategoryTotals = (categories: CategoryNode[] | undefined, index: number) => {
  if (!categories) return { closing_dr: 0, closing_cr: 0 }

  const calculateNodeTotal = (node: CategoryNode): { closing_dr: number, closing_cr: number } => {
    // Get direct total from the node
    const nodeTotal = node.total?.[index] || { closing_dr: 0, closing_cr: 0 }

    // Calculate totals from children recursively
    const childrenTotal = node.children.reduce((acc, child) => {
      const childTotal = calculateNodeTotal(child)
      return {
        closing_dr: acc.closing_dr + (childTotal.closing_dr || 0),
        closing_cr: acc.closing_cr + (childTotal.closing_cr || 0),
      }
    }, { closing_dr: 0, closing_cr: 0 })

    // Combine node total with children total
    return {
      closing_dr: (nodeTotal.closing_dr || 0) + childrenTotal.closing_dr,
      closing_cr: (nodeTotal.closing_cr || 0) + childrenTotal.closing_cr,
    }
  }

  // Calculate total for all top-level categories
  return categories.reduce((acc, category) => {
    const categoryTotal = calculateNodeTotal(category)
    return {
      closing_dr: acc.closing_dr + categoryTotal.closing_dr,
      closing_cr: acc.closing_cr + categoryTotal.closing_cr,
    }
  }, { closing_dr: 0, closing_cr: 0 })
}

const getAmountWithSuffix = (amount: number) => {
  if (amount === 0) {
    return '0'
  } else if (amount > 0) {
    return `${amount.toFixed(2)} cr`
  } else {
    return `${(amount * -1).toFixed(2)} dr`
  }
}

// Add computed property for Cost of Sales
const costOfSales = computed(() => {
  if (!categoryTree.value) return []

  return columns.value.map((_, index) => {
    const purchase = categoryTree.value?.purchase?.[0]?.total[index] || { closing_dr: 0, closing_cr: 0 }
    const directExpense = categoryTree.value?.direct_expense?.[0]?.total[index] || { closing_dr: 0, closing_cr: 0 }
    const openingStock = extraData.value.opening_stock[index] || 0
    const closingStock = extraData.value.closing_stock[index] || 0

    return purchase.closing_dr + directExpense.closing_dr
      - (purchase.closing_cr + directExpense.closing_cr)
      + openingStock - closingStock
  })
})
</script>

<template>
  <div class="q-pa-md">
    <div class="q-px-md q-pb-md">
      <div class="flex items-center justify-between gap-2">
        <div class="flex gap-x-6 gap-y-2 items-center">
          <div>
            <DateRangePicker
              v-model:end-date="fields.end_date"
              v-model:start-date="fields.start_date"
              :focus-on-mount="true"
              :hide-btns="true"
            />
          </div>
          <q-btn
            v-if="fields.start_date || fields.end_date"
            class="f-reset-btn"
            color="red"
            icon="close"
            @click="fields = { start_date: null, end_date: null }"
          />
          <q-btn
            class="f-submit-btn"
            color="green"
            label="fetch"
            :disable="!fields.start_date && !fields.end_date ? true : false"
            :loading="isLoading"
            @click="updateData"
          />
        </div>
        <div v-if="!isLoading" class="flex gap-6">
          <q-btn icon="settings" title="Config">
            <q-menu>
              <div class="menu-wrapper" style="width: min(300px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">
                    Config
                  </h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_accounts" label="Hide Accounts?" />
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_categories" label="Hide Categories?" />
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_sums" label="Hide Sums?" />
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_zero_balance" label="Hide accounts without balance?" />
                  </div>
                </div>
              </div>
            </q-menu>
          </q-btn>
          <q-btn
            class="export-btn"
            color="blue"
            icon-right="download"
            label="Export Xls"
            @click="onDownloadXls"
          />
        </div>
      </div>
    </div>
    <div class="flex gap-2">
      <q-markup-table id="tableRef" class="grow">
        <thead>
          <tr v-if="!isLoading">
            <th class="text-left"></th>
            <th v-for="column in columns" :key="column.start_date" class="text-left">
              {{ getLocalDate(column.start_date) }} -
              {{ getLocalDate(column.end_date) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <template v-if="!isLoading && categoryTree">
            <template v-if="categoryTree?.revenue">
              <AccountBalanceTableNode
                v-for="category in [
                  {
                    id: 9999999,
                    name: 'Revenue',
                    children: categoryTree.revenue,
                    accounts: [],
                    total: columns.map((_, index) => {
                      const totals = calculateCategoryTotals(categoryTree.revenue, index)
                      return {
                        closing_dr: totals.closing_dr,
                        closing_cr: totals.closing_cr,
                      }
                    }),
                  },
                ]"
                :key="category.id"
                name="Revenue"
                :config="config"
                :hide-empty-categories="false"
                :item="category"
                :root="true"
                :unlink-parent="true"
              />
            </template>

            <template
              v-if="
                categoryTree?.direct_expense"
            >
              <AccountBalanceTableNode
                v-for="category in [
                  {
                    id: 1,
                    name: 'Cost of Sales',
                    children: [...categoryTree.direct_expense],
                    accounts: [],
                    total: costOfSales.map(amount => ({
                      closing_dr: amount < 0 ? Math.abs(amount) : 0,
                      closing_cr: amount > 0 ? amount : 0,
                    })),
                  },
                ]"
                :key="category.id"
                name="Cost of Sales"
                :config="config"
                :hide-empty-categories="false"
                :item="category"
                :root="true"
              >
                <template #custom>
                  <tr>
                    <td>
                      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                      <span>COGS</span>
                    </td>
                    <td
                      v-for="(amount, index) in costOfSales"
                      :key="index"
                      class="text-left"
                    >
                      {{ getAmountWithSuffix(amount) }}
                    </td>
                  </tr>
                </template>
              </AccountBalanceTableNode>
            </template>

            <!-- Gross Profit -->
            <tr>
              <td class="text-weight-medium">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span>Gross Profit</span>
              </td>
              <td
                v-for="(profit, index) in grossProfit"
                :key="index"
                class="text-left"
              >
                {{ getAmountWithSuffix(profit) }}
              </td>
            </tr>

            <!-- Other Income -->
            <template v-if="categoryTree?.other_income">
              <AccountBalanceTableNode
                v-for="category in [
                  {
                    id: 999999,
                    name: 'Other Income',
                    children: categoryTree.other_income,
                    accounts: [],
                    total: columns.map((_, index) => {
                      const totals = calculateCategoryTotals(categoryTree.other_income, index)
                      return {
                        closing_dr: totals.closing_dr,
                        closing_cr: totals.closing_cr,
                      }
                    }),
                  },
                ]"
                :key="category.id"
                name="Other Income"
                :config="config"
                :hide-empty-categories="false"
                :item="category"
                :root="true"
                :unlink-parent="true"
              />
            </template>

            <!-- Operating Expense -->
            <template v-if="categoryTree?.operating_expense">
              <AccountBalanceTableNode
                v-for="category in [
                  {
                    id: 99999999,
                    name: 'Operating Expense',
                    children: categoryTree.operating_expense,
                    accounts: [],
                    total: columns.map((_, index) => {
                      const totals = calculateCategoryTotals(categoryTree.operating_expense, index)
                      return {
                        closing_dr: totals.closing_dr,
                        closing_cr: totals.closing_cr,
                      }
                    }),
                  },
                ]"
                :key="category.id"
                name="Operating Expense"
                :config="config"
                :hide-empty-categories="false"
                :item="category"
                :root="true"
                :unlink-parent="true"
              />
            </template>

            <!-- Operating Profit (EBITA) = 3 + 4 - 5 -->
            <tr>
              <td class="text-weight-medium">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span>Operating Profit (EBITA)</span>
              </td>
              <td
                v-for="(profit, index) in operatingProfit"
                :key="index"
                class="text-left"
              >
                {{ getAmountWithSuffix(profit) }}
              </td>
            </tr>

            <!-- Interest Income -->
            <template v-if="categoryTree?.interest_income">
              <AccountBalanceTableNode
                v-for="category in [
                  {
                    id: 9999998,
                    name: 'Interest Income',
                    children: categoryTree.interest_income,
                    accounts: [],
                    total: columns.map((_, index) => {
                      const totals = calculateCategoryTotals(categoryTree.interest_income, index)
                      return {
                        closing_dr: totals.closing_dr,
                        closing_cr: totals.closing_cr,
                      }
                    }),
                  },
                ]"
                :key="category.id"
                name="Interest Income"
                :config="config"
                :hide-empty-categories="false"
                :item="category"
                :root="true"
                :unlink-parent="true"
              />
            </template>

            <!-- Interest Expense -->
            <template v-if="categoryTree?.interest_expense">
              <AccountBalanceTableNode
                v-for="category in [
                  {
                    id: 9999997,
                    name: 'Interest Expense',
                    children: categoryTree.interest_expense,
                    accounts: [],
                    total: columns.map((_, index) => {
                      const totals = calculateCategoryTotals(categoryTree.interest_expense, index)
                      return {
                        closing_dr: totals.closing_dr,
                        closing_cr: totals.closing_cr,
                      }
                    }),
                  },
                ]"
                :key="category.id"
                name="Interest Expense"
                :config="config"
                :hide-empty-categories="false"
                :item="category"
                :root="true"
                :unlink-parent="true"
              />
            </template>

            <!-- 6. Earnings Before Taxes = 6 + 7 - 8 - 9 -->
            <tr>
              <td class="text-weight-medium">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span>Earnings Before Taxes</span>
              </td>
              <td
                v-for="(earnings, index) in earningsBeforeTaxes"
                :key="index"
                class="text-left"
              >
                {{ getAmountWithSuffix(earnings) }}
              </td>
            </tr>

            <!-- Taxes -->
            <tr>
              <td class="text-weight-medium">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span>Taxes</span>
              </td>
              <td
                v-for="(tax, index) in taxes"
                :key="index"
                class="text-left"
              >
                {{ getAmountWithSuffix(tax) }}
              </td>
            </tr>
            <!-- Net Income = 10 - 11 -->
            <tr>
              <td class="text-weight-medium">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span>Net Income</span>
              </td>
              <td
                v-for="(income, index) in netIncome"
                :key="index"
                class="text-left"
              >
                {{ getAmountWithSuffix(income) }}
              </td>
            </tr>
          </template>
          <!-- Show loading -->
          <template v-else>
            <tr>
              <td class="text-center py-6 text-gray-600 my-5" colspan="2">
                <q-spinner-gears size="50px" />
              </td>
            </tr>
          </template>
        </tbody>
      </q-markup-table>
      <q-btn
        v-if="!isLoading"
        class="m-none q-pa-sm h-fit"
        color="green"
        icon="add"
        title="Add Column"
      >
        <q-menu>
          <div class="menu-wrapper" style="width: min(300px, 90vw)">
            <div style="border-bottom: 1px solid lightgrey">
              <h6 class="q-ma-md text-grey-9">
                Add Column
              </h6>
            </div>
            <div class="q-mx-md row q-gutter-md q-mt-xs q-mb-md">
              <DateRangePicker
                id="add-column"
                v-model:end-date="column.end_date"
                v-model:start-date="column.start_date"
                :hide-btns="true"
              />
              <q-btn color="green" label="Filter" @click="addColumn" />
              <q-btn color="red" icon="close" @click="column = { start_date: null, end_date: null }" />
            </div>
          </div>
        </q-menu>
      </q-btn>
    </div>
  </div>
</template>
