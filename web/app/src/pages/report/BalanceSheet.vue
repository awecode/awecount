<template>
  <div class="q-pa-md">
    <div class="q-px-md q-pb-md">
      <div class="flex items-center justify-between gap-2">
        <div class="flex gap-x-6 gap-y-2 items-center">
          <div>
            <DateRangePicker
              v-model:startDate="fields.start_date"
              v-model:endDate="fields.end_date"
              :hide-btns="true"
              :focusOnMount="true"
            />
          </div>
          <q-btn
            v-if="fields.start_date || fields.end_date"
            color="red"
            icon="close"
            @click="fields = { start_date: null, end_date: null }"
            class="f-reset-btn"
          ></q-btn>
          <q-btn
            :disable="!fields.start_date && !fields.end_date ? true : false"
            color="green"
            label="fetch"
            @click="updateData"
            class="f-submit-btn"
          ></q-btn>
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
                    <q-checkbox
                      v-model="config.hide_accounts"
                      label="Hide Accounts?"
                    ></q-checkbox>
                  </div>
                  <div class="q-pb-sm">
                    <q-checkbox
                      v-model="config.hide_sums"
                      label="Hide Sums?"
                    ></q-checkbox>
                  </div>
                  <!-- <div class="q-pb-sm">
                    <q-checkbox
                      v-model="config.show_opening_closing_dr_cr"
                      label="Show Opening Closing Dr/Cr?"
                    ></q-checkbox>
                  </div> -->
                  <div class="q-pb-sm">
                    <q-checkbox
                      v-model="config.hide_zero_balance"
                      label="Hide accounts without balance?"
                    ></q-checkbox>
                  </div>
                </div>
              </div>
            </q-menu>
          </q-btn>
          <q-btn
            color="blue"
            label="Export Xls"
            icon-right="download"
            @click="onDownloadXls"
            class="export-btn"
          />
        </div>
      </div>
    </div>
    <div class="flex gap-2">
      <q-markup-table id="tableRef" separator="none" class="grow">
        <thead>
          <tr v-if="!isLoading">
            <th class="text-left"></th>
            <th
              class="text-left"
              v-for="column in columns"
              :key="column.start_date"
            >
              {{ getLocalDate(column.start_date) }} -
              {{ getLocalDate(column.end_date) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <template v-if="!isLoading">
            <AccountBalanceTableNode
              v-for="category in categoryTree"
              :key="category.id"
              :item="category"
              :root="true"
              :accounts="accounts"
              :category_accounts="category_accounts"
              :config="config"
              :is-balance-sheet="true"
            ></AccountBalanceTableNode>
          </template>
          <tr>
            <td class="text-weight-medium">
              <span>Total Liabilities and Equity</span>
            </td>
            <td
              class="text-left text-weight-medium"
              v-for="total in categoryTree
                ?.filter(
                  (category) =>
                    category.system_code === 'LIABILITIES' ||
                    category.system_code === 'EQUITY'
                )
                .reduce(
                  (acc, category) => {
                    category.total.forEach((total, index) => {
                      if (!acc[index]) {
                        acc[index] = { closing_dr: 0, closing_cr: 0 }
                      }
                      acc[index].closing_dr += total.closing_dr
                      acc[index].closing_cr += total.closing_cr
                    })
                    return acc
                  },
                  [{ closing_dr: 0, closing_cr: 0 }]
                )"
              :key="total"
            >
              {{ (total.closing_cr - total.closing_dr).toFixed(2) }}
            </td>
          </tr>
        </tbody>
      </q-markup-table>
      <q-btn
        color="green"
        icon="add"
        class="m-none q-pa-sm h-fit"
        title="Add Column"
        v-if="!isLoading"
      >
        <q-menu>
          <div class="menu-wrapper" style="width: min(300px, 90vw)">
            <div style="border-bottom: 1px solid lightgrey">
              <h6 class="q-ma-md text-grey-9">Add Column</h6>
            </div>
            <div class="q-mx-md row q-gutter-md q-mt-xs q-mb-md">
              <DateRangePicker
                v-model:startDate="column.start_date"
                v-model:endDate="column.end_date"
                :hide-btns="true"
                id="add-column"
              />
              <q-btn color="green" label="Filter" @click="addColumn"></q-btn>
              <q-btn
                color="red"
                icon="close"
                @click="column = { start_date: null, end_date: null }"
              ></q-btn>
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

const route = useRoute()
const router = useRouter()
const config = ref({
  hide_accounts: false,
  hide_sums: false,
  hide_zero_balance: false,
})
const column = ref({
  start_date: null as null | string,
  end_date: null as null | string,
})
const category_accounts = ref<Record<string, string[]>>({})

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

const $q = useQuasar()
const columns = ref<(typeof column.value)[]>([])
const accounts = ref<Record<number, Account>>({})
const isLoading = ref(false)
const fields = ref<{
  start_date: string | null
  end_date: string | null
}>({
  start_date: null,
  end_date: null,
})
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

const categoryEndpoint = `/api/company/${route.params.company}/full-category-tree/`
useApi(categoryEndpoint, { method: 'GET' })
  .then((data) => {
    categoryTree.value = data
  })
  .catch((error) => {
    console.log('err fetching data', error)
  })

const categoryTree = ref<CategoryNode[] | null>(null)

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

const fetchData = () => {
  isLoading.value = true
  const endpoint = `/api/company/${route.params.company}/balance-sheet/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
  useApi(endpoint)
    .then((data) => {
      if (!categoryTree.value) {
        return
      }

      // for (const categoryGroup of Object.values(categoryTree.value)) {
      mapAccountsToCategories(categoryTree.value, data)
      // }
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

  const endpoint = `/api/company/${route.params.company}/balance-sheet/?start_date=${column.value.start_date}&end_date=${column.value.end_date}`

  try {
    const data = await useApi(endpoint) // Fetch data
    updateAccountsAndRecalculateTotals(
      categoryTree.value!,
      data,
      columns.value.length
    )

    // Add new column
    columns.value.push({
      start_date: column.value.start_date,
      end_date: column.value.end_date,
    })

    isLoading.value = false
  } catch (err) {
    console.error('Error fetching data:', err)
  }
}

const onDownloadXls = async () => {
  // TODO: add download xls link
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
  XLSX.writeFileXLSX(workbook, 'BalanceSheet.xls')
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
  router.push({ path: `/${route.params.company}/reports/balance-sheet/`, query })
  fetchData()
}
if (route.query.start_date && route.query.end_date) {
  fields.value.start_date = route.query.start_date
  fields.value.end_date = route.query.end_date
  fetchData()
}
</script>