<script setup lang="ts">
import { Ref } from 'vue'
import checkPermissions from 'src/composables/checkPermissions'

interface SystemTransactionData {
  id: number
  date: string
  dr_amount: string
  cr_amount: string
  source_type: string
  source_id: number
  counterpart_accounts: {
    account_id: number
    account_name: string
    dr_amount: string
    cr_amount: string
  }[]
}

interface StatementTransactionData {
  id: number
  date: string
  dr_amount: string
  cr_amount: string
  balance: string
  description: string
  transaction_ids: number[]
}

const props = defineProps({
  systemTransactionData: {
    type: Array<SystemTransactionData>,
    required: true,
  },
  statementTransactionData: {
    type: Array<StatementTransactionData>,
    required: true,
  },
  acceptableDifference: {
    type: Number,
    default: 0.01,
  },
})

interface GroupedTransaction {
  statementTransactions: StatementTransactionData[]
  systemTransactions: SystemTransactionData[]
}

const groupedTransactions: Ref<GroupedTransaction[]> = ref([])
const unmatchedStatementTransactions: Ref<StatementTransactionData[]> = ref([])
const unmatchedSystemTransactions: Ref<SystemTransactionData[]> = ref([])

// Create comprehensive maps to track matches
const systemToStatementsMap = new Map()
const statementToSystemsMap = new Map()

// Comprehensive matching function
const findMatchingTransactions = () => {
  // Reset maps
  systemToStatementsMap.clear()
  statementToSystemsMap.clear()

  // First pass: Find all possible matches
  props.statementTransactionData.forEach(statementTransaction => {
    const matchedSystemTransactions = props.systemTransactionData.filter(
      systemTransaction =>
        statementTransaction.transaction_ids.includes(systemTransaction.id)
    )

    if (matchedSystemTransactions.length > 0) {
      // Map statementTransaction to matched systemTransactions
      statementToSystemsMap.set(statementTransaction, matchedSystemTransactions)

      // Map each systemTransaction to the current statementTransaction
      matchedSystemTransactions.forEach(systemTransaction => {
        if (!systemToStatementsMap.has(systemTransaction)) {
          systemToStatementsMap.set(systemTransaction, [])
        }
        systemToStatementsMap.get(systemTransaction).push(statementTransaction)
      })
    }
  })

  // Merge algorithm
  const mergedGroups: GroupedTransaction[] = []
  const processedStatements = new Set()
  const processedSystems = new Set()

  // Helper function to merge or create a new group
  const mergeOrCreateGroup = (statementTransactions: StatementTransactionData[], systemTransactions: SystemTransactionData[]) => {
    // Check if there's an existing group with any of these transactions
    for (let group of mergedGroups) {
      const hasCommonStatement = statementTransactions.some(st =>
        group.statementTransactions.some(gst => gst.id === st.id)
      )
      const hasCommonSystem = systemTransactions.some(sys =>
        group.systemTransactions.some(gsys => gsys.id === sys.id)
      )

      if (hasCommonStatement || hasCommonSystem) {
        // Merge transactions
        statementTransactions.forEach(st => {
          if (!group.statementTransactions.some(gst => gst.id === st.id)) {
            group.statementTransactions.push(st)
          }
        })
        systemTransactions.forEach(sys => {
          if (!group.systemTransactions.some(gsys => gsys.id === sys.id)) {
            group.systemTransactions.push(sys)
          }
        })
        return true
      }
    }

    // If no existing group, create a new one
    mergedGroups.push({
      statementTransactions,
      systemTransactions
    })
    return false
  }

  // Process system to statement mappings
  systemToStatementsMap.forEach((statementTransactions, systemTransaction) => {
    if (!processedSystems.has(systemTransaction)) {
      mergeOrCreateGroup(statementTransactions, [systemTransaction])
      processedSystems.add(systemTransaction)
      statementTransactions.forEach((st: Record<string, string>) => processedStatements.add(st))
    }
  })

  // Process statement to system mappings
  statementToSystemsMap.forEach((systemTransactions, statementTransaction) => {
    if (!processedStatements.has(statementTransaction)) {
      mergeOrCreateGroup([statementTransaction], systemTransactions)
      processedStatements.add(statementTransaction)
      systemTransactions.forEach((st: SystemTransactionData) => processedSystems.add(st))
    }
  })

  // Collect unmatched transactions
  unmatchedSystemTransactions.value = props.systemTransactionData.filter(
    systemTransaction => !processedSystems.has(systemTransaction)
  )

  unmatchedStatementTransactions.value = props.statementTransactionData.filter(
    statementTransaction => !processedStatements.has(statementTransaction)
  )

  return mergedGroups
}

// Generate grouped transactions
groupedTransactions.value = findMatchingTransactions()

const statementSearchBy = ref('Any')
const systemSearchBy = ref('Any')
const searchByOptionsForStatament = ['Any', 'Date', 'Amount', 'Description']
const searchByOptionsForSystem = ['Any', 'Date', 'Amount', 'Account']


const filteredUnmatchedSystemTransactions = ref(unmatchedSystemTransactions.value)
const filteredUnmatchedStatementTransactions = ref(unmatchedStatementTransactions.value)
const searchStatement = ref('')
const searchSystem = ref('')

const searchInUnmatchedSystemTransactions = (search: string | null) => {
  if (!search) {
    filteredUnmatchedSystemTransactions.value = unmatchedSystemTransactions.value
    return
  }
  search = search.toLowerCase()

  if (systemSearchBy.value === 'Any') {
    const matchedSystemTransactions = unmatchedSystemTransactions.value.filter(
      systemTransaction =>
        String(systemTransaction.dr_amount).toLowerCase().includes(search) ||
        String(systemTransaction.cr_amount).toLowerCase().includes(search) ||
        String(systemTransaction.date).toLowerCase().includes(search) ||
        systemTransaction.counterpart_accounts.some(
          counterpart =>
            counterpart.account_name.toLowerCase().includes(search) ||
            String(counterpart.dr_amount).toLowerCase().includes(search) ||
            String(counterpart.cr_amount).toLowerCase().includes(search)
        )
    )
    filteredUnmatchedSystemTransactions.value = matchedSystemTransactions
    return
  }
  else if (systemSearchBy.value === 'Date') {
    const matchedSystemTransactions = unmatchedSystemTransactions.value.filter(
      systemTransaction =>
        String(systemTransaction.date).toLowerCase().includes(search)
    )
    filteredUnmatchedSystemTransactions.value = matchedSystemTransactions
    return
  }
  else if (systemSearchBy.value === 'Amount') {
    const matchedSystemTransactions = unmatchedSystemTransactions.value.filter(
      systemTransaction =>
        String(systemTransaction.dr_amount).toLowerCase().includes(search) ||
        String(systemTransaction.cr_amount).toLowerCase().includes(search)
    )
    filteredUnmatchedSystemTransactions.value = matchedSystemTransactions
    return
  }
  else if (systemSearchBy.value === 'Account') {
    const matchedSystemTransactions = unmatchedSystemTransactions.value.filter(
      systemTransaction =>
        systemTransaction.counterpart_accounts.some(
          counterpart =>
            counterpart.account_name.toLowerCase().includes(search)
        )
    )
    filteredUnmatchedSystemTransactions.value = matchedSystemTransactions
    return
  }


}

const searchInUnmatchedStatementTransactions = (search: string | null) => {
  if (!search) {
    filteredUnmatchedStatementTransactions.value = unmatchedStatementTransactions.value
    return
  }
  search = search.toLowerCase()
  if (statementSearchBy.value === 'Any') {
    const matchedStatementTransactions = unmatchedStatementTransactions.value.filter(
      statementTransaction =>
        String(statementTransaction.dr_amount).toLowerCase().includes(search) ||
        String(statementTransaction.cr_amount).toLowerCase().includes(search) ||
        String(statementTransaction.date).toLowerCase().includes(search) ||
        String(statementTransaction.description).toLowerCase().includes(search)
    )
    filteredUnmatchedStatementTransactions.value = matchedStatementTransactions
    return
  }
  else if (statementSearchBy.value === 'Date') {
    const matchedStatementTransactions = unmatchedStatementTransactions.value.filter(
      statementTransaction =>
        String(statementTransaction.date).toLowerCase().includes(search)
    )
    filteredUnmatchedStatementTransactions.value = matchedStatementTransactions
    return
  }
  else if (statementSearchBy.value === 'Amount') {
    const matchedStatementTransactions = unmatchedStatementTransactions.value.filter(
      statementTransaction =>
        String(statementTransaction.dr_amount).toLowerCase().includes(search) ||
        String(statementTransaction.cr_amount).toLowerCase().includes(search)
    )
    filteredUnmatchedStatementTransactions.value = matchedStatementTransactions
    return
  }
  else if (statementSearchBy.value === 'Description') {
    const matchedStatementTransactions = unmatchedStatementTransactions.value.filter(
      statementTransaction =>
        String(statementTransaction.description).toLowerCase().includes(search)
    )
    filteredUnmatchedStatementTransactions.value = matchedStatementTransactions
    return
  }
}


const calculateTotal = (transactions: SystemTransactionData[] | StatementTransactionData[], forStatement = false) => {
  let cr_amount = 0
  let dr_amount = 0
  for (let transaction of transactions) {
    if (transaction.cr_amount) {
      cr_amount += Number(transaction.cr_amount)
    }
    if (transaction.dr_amount) {
      dr_amount += Number(transaction.dr_amount)
    }
  }
  if (forStatement) {
    return (cr_amount - dr_amount).toFixed(2)
  }
  return (dr_amount - cr_amount).toFixed(2)
}

const calculateTotalFromCounterparts = (counterparts: { dr_amount: string, cr_amount: string }[]) => {
  let cr_amount = 0
  let dr_amount = 0
  for (let counterpart of counterparts) {
    if (counterpart.cr_amount) {
      cr_amount += Number(counterpart.cr_amount)
    }
    if (counterpart.dr_amount) {
      dr_amount += Number(counterpart.dr_amount)
    }
  }
  return (dr_amount - cr_amount).toFixed(2)
}




function getVoucherUrl(row: SystemTransactionData) {
  if (!row.source_id) return ''
  const source_type = row.source_type
  if (source_type === 'Sales Voucher')
    return `/sales-voucher/${row.source_id}/view/`
  if (source_type === 'Purchase Voucher')
    return `/purchase-voucher/${row.source_id}/view`
  if (source_type === 'Journal Voucher')
    return `/journal-voucher/${row.source_id}/view`
  if (source_type === 'Credit Note')
    return `/credit-note/${row.source_id}/view`
  if (source_type === 'Debit Note')
    return `/debit-note/${row.source_id}/view`
  // if (source_type === 'Tax Payment') return 'Tax Payment Edit'
  // TODO: add missing links
  if (source_type === 'Cheque Deposit')
    return `/cheque-deposit/${row.source_id}/view/`
  if (source_type === 'Payment Receipt')
    return `/payment-receipt/${row.source_id}/view/`
  if (source_type === 'Cheque Issue')
    return `/cheque-issue/${row.source_id}/`
  if (source_type === 'Challan') return `/challan/${row.source_id}/`
  if (source_type === 'Account Opening Balance')
    return `/account-opening-balance/${row.source_id}/`
  if (source_type === 'Item') return `/items/details/${row.source_id}/`
  // added
  if (source_type === 'Fund Transfer')
    return `/fund-transfer/${row.source_id}/`
  if (source_type === 'Bank Cash Deposit')
    return `/bank/cash/cash-deposit/${row.source_id}/edit/`
  if (source_type === 'Tax Payment') return `/tax-payment/${row.source_id}/`
  if (source_type === 'Inventory Adjustment Voucher') return `/items/inventory-adjustment/${row.source_id}/view/`
  console.error(source_type + ' not handled!')
}
const getPermissionsWithSourceType = {
  'Sales Voucher': 'SalesView',
  'Purchase Voucher': 'PurchaseVoucherView',
  'Journal Voucher': 'JournalVoucherView',
  'Credit Note': 'CreditNoteView',
  'Debit Note': 'DebitNoteView',
  'Cheque Deposit': 'ChequeDepositView',
  'Payment Receipt': 'PaymentReceiptView',
  'Cheque Issue': 'ChequeIssueModify',
  'Challan': 'ChallanModify',
  'Account Opening Balance': 'AccountOpeningBalanceModify',
  'Fund Transfer': 'FundTransferModify',
  'Bank Cash Deposit': 'BankCashDepositModify',
  'Tax Payment': 'TaxPaymentModify',
  'Item': 'ItemView',
  'Inventory Adjustment Voucher': 'InventoryAdjustmentVoucherView'
} as const

const filterSources = (systemTransactions: SystemTransactionData[]): { source_id: number, url: string, source_type: string }[] => {
  const sourceMap = new Map<number, { source_id: number, url: string, source_type: string }>()

  systemTransactions.forEach((transaction: SystemTransactionData) => {
    if (transaction.source_id) {
      // check permission
      const permission = getPermissionsWithSourceType[transaction.source_type as keyof typeof getPermissionsWithSourceType]
      if (checkPermissions(permission)) {
        const url = getVoucherUrl(transaction)
        if (url) {
          // Use source_id as the unique key
          if (!sourceMap.has(transaction.source_id)) {
            sourceMap.set(transaction.source_id, {
              source_id: transaction.source_id,
              source_type: transaction.source_type,
              url,
            })
          }
        }
      }
    }
  })

  return Array.from(sourceMap.values())
}

// Selected transactions tracking
const selectedStatementTransactions: Ref<StatementTransactionData[]> = ref([])
const selectedSystemTransactions: Ref<SystemTransactionData[]> = ref([])

// Select all toggles
const allStatementSelected = computed(() =>
  selectedStatementTransactions.value.length === unmatchedStatementTransactions.value.length
)

const allSystemSelected = computed(() =>
  selectedSystemTransactions.value.length === unmatchedSystemTransactions.value.length
)

// Toggle individual transactions
const toggleStatementTransaction = (transaction: StatementTransactionData) => {
  const index = selectedStatementTransactions.value.findIndex(t => t.id === transaction.id)
  if (index > -1) {
    selectedStatementTransactions.value.splice(index, 1)
  } else {
    selectedStatementTransactions.value.push(transaction)
  }
}

const toggleSystemTransaction = (transaction: SystemTransactionData) => {
  const index = selectedSystemTransactions.value.findIndex(t => t.id === transaction.id)
  if (index > -1) {
    selectedSystemTransactions.value.splice(index, 1)
  } else {
    selectedSystemTransactions.value.push(transaction)
  }
}

// Toggle all transactions
const toggleAllStatementTransactions = () => {
  if (allStatementSelected.value) {
    selectedStatementTransactions.value = []
  } else {
    selectedStatementTransactions.value = [...unmatchedStatementTransactions.value]
  }
}

const toggleAllSystemTransactions = () => {
  if (allSystemSelected.value) {
    selectedSystemTransactions.value = []
  } else {
    selectedSystemTransactions.value = [...unmatchedSystemTransactions.value]
  }
}

// Check if a specific transaction is selected
const isStatementTransactionSelected = (transaction: StatementTransactionData) =>
  selectedStatementTransactions.value.some(t => t.id === transaction.id)

const isSystemTransactionSelected = (transaction: SystemTransactionData) =>
  selectedSystemTransactions.value.some(t => t.id === transaction.id)



const canReconcile = computed(() => {
  return selectedStatementTransactions.value.length > 0 &&
    selectedSystemTransactions.value.length > 0 &&
    Math.abs(Number(calculateTotal(selectedStatementTransactions.value, true)) - Number(calculateTotal(selectedSystemTransactions.value))) < props.acceptableDifference
}
  // also total amount matches
)

const unselectAll = () => {
  selectedStatementTransactions.value = []
  selectedSystemTransactions.value = []
}



const reconcileMatchedTransactions = (matchedTransaction: {
  statementTransactions: StatementTransactionData[]
  systemTransactions: SystemTransactionData[]
}) => {
  console.log('Reconciling:', matchedTransaction)
  useApi('v1/bank-reconciliation/reconcile-transactions/', {
    method: 'POST',
    body: {
      statement_ids: matchedTransaction.statementTransactions.map(t => t.id),
      transaction_ids: matchedTransaction.systemTransactions.map(t => t.id),
    }
  }).then((response) => {
    const index = groupedTransactions.value.findIndex(group => group === matchedTransaction)
    if (index > -1) {
      groupedTransactions.value.splice(index, 1)
    }
  })
}

const reconcile = () => {
  if (selectedStatementTransactions.value.length > 0 || selectedSystemTransactions.value.length > 0) {
    const endpoint = canReconcile ? 'v1/bank-reconciliation/reconcile-with-adjustment/' : 'v1/bank-reconciliation/reconcile-transactions/'
    useApi(endpoint, {
      method: 'POST',
      body: {
        statement_ids: selectedStatementTransactions.value.map(t => t.id),
        transaction_ids: selectedSystemTransactions.value.map(t => t.id),
        narration: 'Test Narration',
      }
    }).then(() => {
      // remove from both unmatched lists
      selectedStatementTransactions.value.forEach(t => {
        const index = unmatchedStatementTransactions.value.findIndex(ut => ut === t)
        if (index > -1) {
          unmatchedStatementTransactions.value.splice(index, 1)
        }
      })
      selectedSystemTransactions.value.forEach(t => {
        const index = unmatchedSystemTransactions.value.findIndex(ut => ut === t)
        if (index > -1) {
          unmatchedSystemTransactions.value.splice(index, 1)
        }
      })
      // remove from selected
      unselectAll()
    }).catch((error) => {
      console.log(error)
    })
  }

}

const unmatchMatchedTransactions = (matchedTransaction: {
  statementTransactions: StatementTransactionData[]
  systemTransactions: SystemTransactionData[]
}) => {
  console.log('Unmatching:', matchedTransaction)
  useApi('v1/bank-reconciliation/unmatch-transactions/', {
    method: 'POST',
    body: {
      statement_ids: matchedTransaction.statementTransactions.map(t => t.id),
    }
  }).then(() => {
    matchedTransaction.statementTransactions.forEach(t => {
      unmatchedStatementTransactions.value.push(t)
    })
    matchedTransaction.systemTransactions.forEach(t => {
      unmatchedSystemTransactions.value.push(t)
    })
    // remove from groupedTransactions
    const index = groupedTransactions.value.findIndex(group => group === matchedTransaction)
    if (index > -1) {
      groupedTransactions.value.splice(index, 1)
    }
  })
}



</script>
<template>
  <div>
    <!-- Unmatched section -->
    <div class="grid grid-cols-2 gap-10">
      <div class="border p-5 bg-gray-100 rounded-lg shadow-md">
        <div class="bg-gray-100 p-4 pt-0 rounded-lg">
          <div class="flex space-x-3 w-fit ml-auto">
            <button @click="unselectAll" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm">
              Unselect All
            </button>
            <button @click="reconcile" :disabled="!selectedStatementTransactions.length && !selectedSystemTransactions.length"
              class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed">
              {{ canReconcile ? 'Reconcile' : 'Reconcile with Adjustments' }}
            </button>
          </div>

          <div class="flex justify-between mt-4 space-x-6">
            <!-- Statement Transactions Summary -->
            <div class="space-y-1">
              <div class="flex items-center">
                <span class="text-lg font-semibold text-blue-700">Statement Transactions</span>
                <span class="text-xs text-blue-500 ml-2 bg-blue-100 px-2 py-1 rounded-full">
                  {{ selectedStatementTransactions.length }}
                </span>
              </div>
              <div class="text-sm text-gray-600">
                Total:
                <span class="font-medium text-blue-600">
                  {{ calculateTotal(selectedStatementTransactions, true) }}
                </span>
              </div>
            </div>

            <!-- Show difference -->
            <div class="text-sm text-center flex flex-col justify-center space-y-1">
              <span class="font-semibold">Difference:</span>
              <div
                :class="Math.abs(Number(calculateTotal(selectedStatementTransactions, true)) - Number(calculateTotal(selectedSystemTransactions))) > props.acceptableDifference ? 'text-red-600' : 'text-green-600'"
                class="font-medium">
                {{ Math.abs(Number(calculateTotal(selectedStatementTransactions, true)) - Number(calculateTotal(selectedSystemTransactions))) }}
              </div>
            </div>

            <!-- System Transactions Summary -->
            <div class="space-y-1">
              <div class="flex items-center">
                <span class="text-lg font-semibold text-green-700">System Transactions</span>
                <span class="text-xs text-green-500 ml-2 bg-green-100 px-2 py-1 rounded-full">
                  {{ selectedSystemTransactions.length }}
                </span>
              </div>
              <div class="text-sm text-gray-600">
                Total:
                <span class="font-medium text-green-600">
                  {{ calculateTotal(selectedSystemTransactions) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <!-- Unmatched Statement Transactions -->
          <!-- add search input field -->
          <div>
            <div class="flex gap-4">
              <!-- q-select -->
              <q-select v-model="statementSearchBy" :options="searchByOptionsForStatament" outlined dense label="Search By" class="w-28" />
              <q-input v-model="searchStatement" :debounce="500" @update:model-value="(value) => searchInUnmatchedStatementTransactions(value as string)" outlined dense placeholder="Search..."
                class="grow mb-2" />
            </div>
            <div class="bg-white rounded-lg shadow-sm border overflow-hidden">
              <div class="px-4 py-3 border-b bg-blue-50 ">
                <h3 class="text-lg my-0 font-semibold text-blue-600">
                  Unmatched Statement Transactions
                  <span class="text-sm text-blue-500 ml-2">({{ filteredUnmatchedStatementTransactions.length }})</span>
                </h3>
                <div class="flex items-center justify-between mt-2">
                  <div>
                    <input type="checkbox" class="px-4 h-4 w-4 text-blue-600 rounded" :checked="allStatementSelected" @change="toggleAllStatementTransactions" />
                    <span class="ml-2 text-sm text-gray-600">Select All</span>
                  </div>
                  <div>
                    <span class="font-medium" :class="Number(calculateTotal(filteredUnmatchedStatementTransactions, true)) < 0 ? 'text-red-500' : 'text-green-500'">{{
                      calculateTotal(filteredUnmatchedStatementTransactions, true)
                      }}</span>
                  </div>
                </div>
              </div>

              <div class="divide-y max-h-[600px] overflow-y-auto text-xs">
                <div v-for="data in filteredUnmatchedStatementTransactions" :key="data.id" class="px-4 hover:bg-gray-50 flex flex-nowrap items-center space-x-3 border-b">
                  <input type="checkbox" class="px-4 h-4 w-4 text-green-600 rounded" :checked="isStatementTransactionSelected(data)" @change="toggleStatementTransaction(data)" />
                  <div :key="data.id" class="py-3 pl-2 pr-0 border-gray-200 hover:bg-gray-50 transition-colors duration-200 relative grow">
                    <div class="flex justify-between mb-1">
                      <span class="text-gray-500">{{ data.date }}</span>
                      <div class="font-medium">
                        <span v-if="data.dr_amount" class="text-red-500 ">-{{ data.dr_amount }}</span>
                        <span v-if="data.cr_amount" class="text-green-500">+{{ data.cr_amount }}</span>
                      </div>
                    </div>
                    <div class="text-gray-600">{{ data.description }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- --------------------------------------------------------------                  Unmatched System Transactions                      -------------------------------------------------------------------------------- -->

          <div>
            <div class="flex gap-4">
              <!-- q-select -->
              <q-select v-model="systemSearchBy" :options="searchByOptionsForSystem" outlined dense label="Search By" class="w-28" />
              <q-input v-model="searchSystem" :debounce="500" @update:model-value="(value) => searchInUnmatchedSystemTransactions(value as string)" outlined dense placeholder="Search..."
                class="grow mb-2" />
            </div>
            <div class="bg-white rounded-lg shadow-sm border overflow-hidden">
              <div class="px-4 py-3 border-b bg-green-50">
                <h3 class="text-lg my-0 font-semibold text-green-600">
                  Unmatched System Transactions
                  <span class="text-sm text-green-500 ml-2">({{ filteredUnmatchedSystemTransactions.length }})</span>
                </h3>
                <div class="flex items-center justify-between mt-2">
                  <div class="flex items-centers">
                    <input type="checkbox" class="px-4 h-4 w-4 text-green-600 rounded" :checked="allSystemSelected" @change="toggleAllSystemTransactions" />
                    <span class="ml-2 text-sm text-gray-600">Select All</span>
                  </div>
                  <div>
                    <span class="font-medium" :class="Number(calculateTotal(filteredUnmatchedSystemTransactions)) < 0 ? 'text-red-500' : 'text-green-500'">{{
                      calculateTotal(filteredUnmatchedSystemTransactions)
                      }}</span>
                  </div>
                </div>
              </div>

              <div class="divide-y max-h-[600px] overflow-y-auto">
                <div v-for="data in filteredUnmatchedSystemTransactions" :key="data.id" class="flex items-center border-b px-3 py-3 hover:bg-gray-50 transition-colors duration-200">
                  <input type="checkbox" class="h-5 w-5 mr-3 text-green-600 rounded focus:ring-2 focus:ring-green-500" :checked="isSystemTransactionSelected(data)"
                    @change="toggleSystemTransaction(data)" />

                  <div class="flex-grow min-w-0">
                    <!-- Transaction Header -->
                    <div class="flex justify-between items-center mb-2">
                      <span class="text-xs text-gray-500">{{ data.date }}</span>

                      <router-link v-if="data.source_type && data.source_id && checkPermissions(getPermissionsWithSourceType[data.source_type as keyof typeof getPermissionsWithSourceType])"
                        :to="getVoucherUrl(data) as string" target="_blank" class="text-blue-800 text-xs hover:underline">
                        {{ data.source_type }}
                      </router-link>
                    </div>

                    <!-- Counterpart Accounts -->
                    <div class="space-y-1">
                      <div v-for="counterpart in data.counterpart_accounts" :key="counterpart.account_id" class="flex justify-between items-center text-xs">
                        <div class="text-gray-700 truncate pr-2">
                          {{ counterpart.account_name }}
                        </div>

                        <div class="flex space-x-2">
                          <span v-if="counterpart.dr_amount" class="text-red-600 font-medium">
                            -{{ counterpart.dr_amount }}
                          </span>
                          <span v-if="counterpart.cr_amount" class="text-green-600 font-medium">
                            +{{ counterpart.cr_amount }}
                          </span>
                        </div>
                      </div>
                    </div>

                    <!-- Total for Multiple Counterparts -->
                    <div v-if="data.counterpart_accounts.length > 1" class="border-t text-right text-xs w-fit ml-auto">
                      <span v-if="data.dr_amount" class="text-green-500 font-semibold">
                        +{{ data.dr_amount }}
                      </span>
                      <span v-if="data.cr_amount" class="text-red-500 font-semibold ml-2">
                        -{{ data.cr_amount }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="container mx-auto">
        <div class="bg-white shadow-lg rounded-lg overflow-hidden border">
          <div class="p-4 bg-gray-50 max-h-[800px] overflow-y-auto">
            <div v-for="(data, index) in groupedTransactions" :key="index" class="border-b-2 mb-5 pb-5">


              <div class="grid grid-cols-2 gap-4">
                <!-- Statement Transactions -->
                <div class="flex flex-col">
                  <div class="bg-white border rounded-lg shadow-sm overflow-hidden grow">
                    <div class="px-4 py-2 border-b bg-blue-50 text-blue-700 font-semibold">
                      Statement
                    </div>
                    <div class="divide-y text-xs">
                      <div v-for="transaction in data.statementTransactions" :key="transaction.id" class="px-4 py-2.5">
                        <div class="flex justify-between mb-1">
                          <span class="text-gray-500">{{ transaction.date }}</span>
                          <div class="font-medium">
                            <span v-if="transaction.dr_amount" class="text-red-500">-{{ transaction.dr_amount }}</span>
                            <span v-if="transaction.cr_amount" class="text-green-500">+{{ transaction.cr_amount }}</span>
                          </div>
                        </div>
                        <div class="text-gray-600">{{ transaction.description }}</div>
                      </div>
                    </div>

                  </div>
                  <div class="px-4 py-2 text-right">
                    <span :class="Number(calculateTotal(data.statementTransactions, true)) < 0 ? 'text-red-500' : 'text-green-500'">{{ calculateTotal(data.statementTransactions, true) }}</span>
                  </div>
                </div>

                <!-- System Transactions -->
                <div class="flex flex-col">
                  <div class="bg-white border rounded-lg shadow-sm overflow-hidden grow">
                    <div class="px-4 py-2 border-b bg-green-50 text-green-700 font-semibold">
                      System
                      <!-- Add links -->
                      <span v-for="source, index in filterSources(data.systemTransactions)" :key="source.source_id">
                        <router-link target="_blank" :to="source.url" class="text-blue-800 decoration-none text-xs">
                          {{ source.source_type }}
                        </router-link>
                        <span v-if="index < filterSources(data.systemTransactions).length - 1">, </span>
                      </span>

                    </div>
                    <div class="divide-y text-sm">
                      <div v-for="transaction, index in data.systemTransactions" :key="transaction.id" class="px-4 py-3  border-gray-200 hover:bg-gray-50 transition-colors duration-200 relative group"
                        :class="{ 'border-b': index !== data.systemTransactions.length - 1 }">

                        <div class="text-xs">
                          <div class="text-gray-500">{{ transaction.date }}</div>

                          <div v-for="counterpart in transaction.counterpart_accounts" :key="counterpart.account_id" class="flex justify-between">
                            <div class="text-gray-700 truncate flex-grow mr-2">
                              {{ counterpart.account_name }}
                            </div>
                            <div class="flex space-x-2">
                              <span v-if="counterpart.dr_amount" class="text-red-600 font-medium">
                                -{{ counterpart.dr_amount }}
                              </span>
                              <span v-if="counterpart.cr_amount" class="text-green-600 font-medium">
                                +{{ counterpart.cr_amount }}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="px-4 py-2 text-right">
                    <span :class="Number(calculateTotalFromCounterparts(data.systemTransactions)) < 0 ? 'text-red-500' : 'text-green-500'">{{ calculateTotalFromCounterparts(data.systemTransactions)
                      }}</span>
                  </div>
                </div>
              </div>
              <div class="flex justify-end space-x-3">
                <button @click="
                  reconcileMatchedTransactions(data)
                  " class="px-3 py-1.5 bg-green-500 text-white text-sm rounded-md hover:bg-green-600 transition-colors">
                  Reconcile
                </button>
                <button @click="unmatchMatchedTransactions(data)" class="px-3 py-1.5 bg-red-500 text-white text-sm rounded-md hover:bg-red-600 transition-colors">
                  Unmatch
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<style scoped>
.border {
  border: 1px solid black !important;
}

.border-b {
  border-bottom: 1px solid black !important;
}

.border-b-2 {
  border-bottom: 2px solid black !important;
}

.border-t {
  border-top: 1px solid black !important;
}
</style>
