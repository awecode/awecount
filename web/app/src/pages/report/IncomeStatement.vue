<template>
  <div class="q-pa-md">
    <div class="q-px-md q-pb-md">
      <div class="flex items-center justify-between gap-2">
        <div class="flex gap-x-6 gap-y-2 items-center">
          <div>
            <DateRangePicker v-model:startDate="fields.start_date" v-model:endDate="fields.end_date" :hide-btns="true"
              :focusOnMount="true" />
          </div>
          <q-btn v-if="fields.start_date || fields.end_date" color="red" icon="close"
            @click="fields = { start_date: null, end_date: null }" class="f-reset-btn"></q-btn>
          <q-btn :disable="!fields.start_date && !fields.end_date ? true : false" color="green" label="fetch"
            @click="updateData" :loading="isLoading" class="f-submit-btn"></q-btn>
        </div>
        <div class="flex gap-6" v-if="!isLoading">
          <q-btn icon="settings" title="Config">
            <q-menu>
              <div class="menu-wrapper" style="width: min(300px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Config</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_accounts" label="Hide Accounts?"></q-checkbox>
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_categories" label="Hide Categories?"></q-checkbox>
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_sums" label="Hide Sums?"></q-checkbox>
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox v-model="config.hide_zero_balance" label="Hide accounts without balance?"></q-checkbox>
                  </div>
                </div>
              </div>
            </q-menu>
          </q-btn>
          <q-btn color="blue" label="Export Xls" icon-right="download" @click="onDownloadXls" class="export-btn" />
        </div>
      </div>
    </div>
    <div class="flex gap-2">
      <q-markup-table id="tableRef" class="grow">
        <thead>
          <tr v-if="!isLoading">
            <th class="text-left"></th>
            <th class="text-left" v-for="column in columns" :key="column.start_date">
              {{ getLocalDate(column.start_date) }} -
              {{ getLocalDate(column.end_date) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <template v-if="!isLoading && categoryTree">
            <template v-if="categoryTree?.['net_sales']">
              <AccountBalanceTableNode v-for="category in categoryTree['net_sales']" :key="category.id" :item="category"
                :root="true" :config="config" :hide-empty-categories="false" name="Net Sales"></AccountBalanceTableNode>
            </template>
            <template v-if="categoryTree?.direct_expense">
              <AccountBalanceTableNode v-for="category in categoryTree.direct_expense" :key="category.id"
                :item="category" :root="true" :config="config" :hide-empty-categories="false" name="Direct Expense">
              </AccountBalanceTableNode>
            </template>
            <template v-if="categoryTree?.purchase">
              <AccountBalanceTableNode v-for="category in categoryTree.purchase" :key="category.id" :item="category"
                :root="true" :config="config" :hide-empty-categories="false" name="Purchase"></AccountBalanceTableNode>
            </template>
            <!-- Opening Stock -->
            <tr>
              <td class="text-weight-medium">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span>Opening Stock</span>
              </td>
              <td class="text-left" v-for="data in extraData.opening_stock" :key="data">
                {{ data?.toFixed(2) }}
              </td>
            </tr>
            <tr>
              <td class="text-weight-medium">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span>Closing Stock</span>
              </td>
              <td class="text-left" v-for="data in extraData.closing_stock" :key="data">
                {{ data?.toFixed(2) }}
              </td>
            </tr>
            <tr>
              <td class="text-weight-medium" style="border-top: 1px solid gray">
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <span>COGS</span>
              </td>
              <td class="text-left" v-for="(data, index) in extraData.closing_stock" style="border-top: 1px solid gray"
                :key="data">
                {{
                  (
                    categoryTree.purchase[0].total[index].closing_dr +
                    categoryTree.direct_expense[0].total[index].closing_dr -
                    (categoryTree.purchase[0].total[index].closing_cr +
                      categoryTree.direct_expense[0].total[index].closing_cr) +
                    extraData.opening_stock[0] -
                    extraData.closing_stock[0]
                  ).toFixed(2)
                }}
              </td>
            </tr>

            <!-- Closing Stock -->

            <template v-if="categoryTree?.['indirect_expense']">
              <AccountBalanceTableNode v-for="category in categoryTree['indirect_expense']" :key="category.id"
                :item="category" :root="true" :config="config" :hide-empty-categories="false" name="Indirect Expense">
              </AccountBalanceTableNode>
            </template>
          </template>
          <!-- Show loading -->
          <template v-else>
            <tr>
              <td colspan="2" class="text-center py-6 text-gray-600 my-5">
                <q-spinner-gears size="50px" />
              </td>
            </tr>
          </template>
        </tbody>
      </q-markup-table>
      <q-btn color="green" icon="add" class="m-none q-pa-sm h-fit" title="Add Column" v-if="!isLoading">
        <q-menu>
          <div class="menu-wrapper" style="width: min(300px, 90vw)">
            <div style="border-bottom: 1px solid lightgrey">
              <h6 class="q-ma-md text-grey-9">Add Column</h6>
            </div>
            <div class="q-mx-md row q-gutter-md q-mt-xs q-mb-md">
              <DateRangePicker v-model:startDate="column.start_date" v-model:endDate="column.end_date" :hide-btns="true"
                id="add-column" />
              <q-btn color="green" label="Filter" @click="addColumn"></q-btn>
              <q-btn color="red" icon="close" @click="column = { start_date: null, end_date: null }"></q-btn>
            </div>
          </div>
        </q-menu>
      </q-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import AccountBalanceTableNode from 'src/components/report/AccountBalanceTableNode.vue'
import DateConverter from 'src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'

type Account = {
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

type CategoryNode = {
  id: number
  name?: string
  code?: string
  children: CategoryNode[]
  system_code?: string | null
  accounts?: Account[] // To hold the mapped accounts
  total: { closing_dr: number; closing_cr: number }[]
}

type CategoryTree = {
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
  return DateConverter.getRepresentation(
    date,
    store.isCalendarInAD ? 'ad' : 'bs'
  )
}

const config = ref({
  hide_accounts: false,
  hide_categories: false,
  hide_sums: false,
  show_opening_closing_dr_cr: false,
  hide_zero_balance: false,
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
  opening_stock: [],
  closing_stock: [],
})

const mapAccountsToCategories = (
  categories: CategoryNode[],
  accounts: Account[]
) => {
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

  const calculateTotalWithChildren = (
    node: CategoryNode
  ): { closing_dr: number; closing_cr: number }[] => {
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
      [{ closing_dr: 0, closing_cr: 0 }]
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
      [{ closing_dr: 0, closing_cr: 0 }]
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
    })
    .catch((err) => console.log(err))
    .finally(() => {
      isLoading.value = false
    })
}

const updateAccountsAndRecalculateTotals = (
  categories: CategoryNode[],
  newAccounts: Account[],
  currentIndex: number
) => {
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
    const newAccountsForCategory = newAccounts.filter(
      (newAccount) => newAccount.category_id === categoryId
    )

    // Update existing accounts
    for (const account of accounts) {
      const matchingNewAccount = newAccountsForCategory.find(
        (newAccount) => newAccount.id === account.id
      )

      if (matchingNewAccount) {
        // Append new transaction data for the current index without altering previous totals
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
      if (!accounts.some((account) => account.id === newAccount.id)) {
        const newTransactionData = Array(currentIndex).fill({
          closing_dr: 0,
          closing_cr: 0,
        })
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
  const calculateTotals = (
    node: CategoryNode
  ): { closing_dr: number; closing_cr: number }[] => {
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
    }, [] as { closing_dr: number; closing_cr: number }[])

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
    }, [] as { closing_dr: number; closing_cr: number }[])

    // Combine current node totals with children totals
    const maxLength = Math.max(currentNodeTotal.length, childrenTotal.length)
    const combinedTotal = Array.from({ length: maxLength }, (_, index) => ({
      closing_dr:
        (currentNodeTotal[index]?.closing_dr || 0) +
        (childrenTotal[index]?.closing_dr || 0),
      closing_cr:
        (currentNodeTotal[index]?.closing_cr || 0) +
        (childrenTotal[index]?.closing_cr || 0),
    }))
    return combinedTotal
  }

  // Update the tree with recalculated totals
  const updateTree = (nodes: CategoryNode[]) => {
    for (const node of nodes) {
      node.accounts = categoryMap.get(node.id) || []
      node.total = calculateTotals(node)
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
  if (
    columns.value.some(
      (col) =>
        col.start_date === column.value.start_date &&
        col.end_date === column.value.end_date
    )
  ) {
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
      updateAccountsAndRecalculateTotals(
        categoryGroup,
        data.accounts,
        columns.value.length
      )
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

const onDownloadXls = async () => {
  const XLSX = await import('xlsx-js-style')
  const elt = document.getElementById('tableRef').children[0]
  const baseUrl = window.location.origin
  replaceHrefAttribute(elt, baseUrl)
  // adding styles
  const worksheet = XLSX.utils.table_to_sheet(elt)
  for (const i in worksheet) {
    if (typeof worksheet[i] != 'object') continue
    let cell = XLSX.utils.decode_cell(i)
    worksheet[i].s = {
      font: { name: 'Courier', sz: 12 },
    }
    if (cell.r == 0) {
      // first row
      worksheet[i].s.font.bold = true
    }
    if (cell.c == 0) {
      // first row
      const td = elt.rows[cell.r].cells[cell.c]
      worksheet[i].s.font.italic = getComputedStyle(td).fontStyle === 'italic'
      //get color and apply to excel
      const hexCode = getComputedStyle(td).color
      const hexArray = hexCode.slice(4, hexCode.length - 1).split(',')
      const numsArray = hexArray.map((e) => Number(e))
      const rgbValue = (
        (1 << 24) |
        (numsArray[0] << 16) |
        (numsArray[1] << 8) |
        numsArray[2]
      )
        .toString(16)
        .slice(1)
      worksheet[i].s.font.color = { rgb: `${rgbValue}` }
    }
    if (cell.r > -1) {
      const td = elt.rows[cell.r].cells[cell.c]
      if (td instanceof HTMLElement)
        worksheet[i].s.font.bold =
          Number(getComputedStyle(td).fontWeight) >= 500
    }
  }
  worksheet['!cols'] = [
    { width: 50 },
    { width: 16 },
    { width: 16 },
    { width: 16 },
    { width: 16 },
    { width: 16 },
    { width: 16 },
    { width: 16 },
    { width: 16 },
    { width: 16 },
    { width: 16 },
  ]
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'sheet_name_here')
  // const excelBuffer = XLSX.write(workbook, {
  //   type: 'buffer',
  //   cellStyles: true,
  // });
  // download Excel
  XLSX.writeFileXLSX(workbook, 'IncomeStatement.xls')
}
// to replace link '/' with base url
const replaceHrefAttribute = (element, baseUrl) => {
  if (!element || !element.childNodes) return
  for (var i = 0; i < element.childNodes.length; i++) {
    var child = element.childNodes[i]
    if (child.tagName === 'A') {
      const link = child.getAttribute('href')
      child.setAttribute('href', baseUrl + `${link}`)
    }
    replaceHrefAttribute(child, baseUrl)
  }
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
</script>