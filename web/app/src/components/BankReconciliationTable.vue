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
  statement_date: string
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

const calculateTotal = (transactions: SystemTransactionData[] | StatementTransactionData[]) => {
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
  return (cr_amount - dr_amount).toFixed(2)
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
  return (cr_amount - dr_amount).toFixed(2)
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
  // if (allStatementSelected.value) {
  //   selectedStatementTransactions.value = []
  // } else {
  //   selectedStatementTransactions.value = [...unmatchedStatementTransactions.value]
  // }
}

const toggleAllSystemTransactions = () => {
  // if (allSystemSelected.value) {
  //   selectedSystemTransactions.value = []
  // } else {
  //   selectedSystemTransactions.value = [...unmatchedSystemTransactions.value]
  // }
}

// Check if a specific transaction is selected
const isStatementTransactionSelected = (transaction: StatementTransactionData) =>
  selectedStatementTransactions.value.some(t => t.id === transaction.id)

const isSystemTransactionSelected = (transaction: SystemTransactionData) =>
  selectedSystemTransactions.value.some(t => t.id === transaction.id)



const canReconcile = computed(() => {
  console.log('canReconcile:', selectedStatementTransactions.value.length > 0 &&
    selectedSystemTransactions.value.length > 0
    && (Number(calculateTotal(selectedStatementTransactions.value)) - Number(calculateTotal(selectedSystemTransactions.value)) == 0))
  return selectedStatementTransactions.value.length > 0 &&
    selectedSystemTransactions.value.length > 0
    && (Number(calculateTotal(selectedStatementTransactions.value)) - Number(calculateTotal(selectedSystemTransactions.value)) == 0)
}
  // also total amount matches
)

const unselectAll = () => {
  selectedStatementTransactions.value = []
  selectedSystemTransactions.value = []
}

const reconcile = () => {
  if (canReconcile.value) {
    // Implement reconciliation logic
    // This might involve matching selected transactions,
    // updating database, etc.
    console.log('Reconciling:', {
      statementTransactions: selectedStatementTransactions.value,
      systemTransactions: selectedSystemTransactions.value
    })

    // Optionally clear selections after reconciliation
    unselectAll()
  }
}

</script>
<template>
  <div>
    <!-- Unmatched section -->
    <div class="grid grid-cols-2 gap-10">
      <div class="border p-5 bg-gray-100 rounded-lg shadow-md">
        <div class="flex justify-between items-center bg-gray-100 p-4 rounded-lg">
          <div class="flex space-x-6">
            <!-- Statement Transactions Summary -->
            <div class="space-y-1">
              <div class="flex items-center">
                <span class="text-lg font-semibold text-blue-700">Statement Transactions</span>
                <span class="text-sm text-blue-500 ml-2 bg-blue-100 px-2 rounded-full">
                  {{ selectedStatementTransactions.length }}
                </span>
              </div>
              <div class="text-sm text-gray-600">
                Total:
                <span class="font-medium text-blue-600">
                  {{ calculateTotal(selectedStatementTransactions) }}
                </span>
              </div>
            </div>

            <!-- System Transactions Summary -->
            <div class="space-y-1">
              <div class="flex items-center">
                <span class="text-lg font-semibold text-green-700">System Transactions</span>
                <span class="text-sm text-green-500 ml-2 bg-green-100 px-2 rounded-full">
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

          <div class="flex space-x-3">
            <button @click="unselectAll" class="px-3 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm">
              Unselect All
            </button>
            {{ canReconcile }}
            <button @click="reconcile" :disabled="!canReconcile"
              class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed">
              Reconcile
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <!-- Unmatched Statement Transactions -->
          <div class="bg-white rounded-lg shadow-sm border">
            <div class="px-4 py-3 border-b bg-blue-50 flex justify-between items-center">
              <h3 class="text-lg font-semibold text-blue-600">
                Unmatched Statement Transactions
                <span class="text-sm text-blue-500 ml-2">({{ unmatchedStatementTransactions.length }})</span>
              </h3>
              <label class="flex items-center">
                <input type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 rounded" :checked="allStatementSelected" @change="toggleAllStatementTransactions" />
                <span class="ml-2 text-sm text-gray-600">Select All</span>
              </label>
            </div>

            <div class="divide-y max-h-96 overflow-y-auto">
              <div v-for="data in unmatchedStatementTransactions" :key="data.id" class="px-4 py-3 hover:bg-gray-50 flex items-center space-x-3">
                <input type="checkbox" class="form-checkbox h-4 w-4 text-blue-600 rounded" :checked="isStatementTransactionSelected(data)" @change="toggleStatementTransaction(data)" />
                <div class="flex-grow">
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-500">{{ data.statement_date }}</span>
                    <div>
                      <span class="text-red-500 mr-2">-{{ data.dr_amount }}</span>
                      <span class="text-green-500">+{{ data.cr_amount }}</span>
                    </div>
                  </div>
                  <div class="text-xs text-gray-500 mt-1">Balance: {{ data.balance }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Unmatched System Transactions -->
          <div class="bg-white rounded-lg shadow-sm border">
            <div class="px-4 py-3 border-b bg-green-50 flex justify-between items-center">
              <h3 class="text-lg font-semibold text-green-600">
                Unmatched System Transactions
                <span class="text-sm text-green-500 ml-2">({{ unmatchedSystemTransactions.length }})</span>
              </h3>
              <label class="flex items-center">
                <input type="checkbox" class="form-checkbox h-4 w-4 text-green-600 rounded" :checked="allSystemSelected" @change="toggleAllSystemTransactions" />
                <span class="ml-2 text-sm text-gray-600">Select All</span>
              </label>
            </div>

            <div class="divide-y max-h-96 overflow-y-auto">
              <div v-for="data in unmatchedSystemTransactions" :key="data.id" class="px-4 py-3 hover:bg-gray-50 flex items-center space-x-3">
                <input type="checkbox" class="form-checkbox h-4 w-4 text-green-600 rounded" :checked="isSystemTransactionSelected(data)" @change="toggleSystemTransaction(data)" />
                <div class="flex-grow">
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-500">{{ data.date }} ({{ data.id }})</span>
                    <div>
                      <span class="text-red-500 mr-2">-{{ data.dr_amount }}</span>
                      <span class="text-green-500">+{{ data.cr_amount }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="container mx-auto p-4">
        <div class="bg-white shadow-lg rounded-lg overflow-hidden">
          <div class="p-4 bg-gray-50">
            <div v-for="(data, index) in groupedTransactions" :key="index" class="space-y-4 border-b mb-5">
              <div class="flex justify-end space-x-3 mb-2">
                <button class="px-3 py-1.5 bg-green-500 text-white text-sm rounded-md hover:bg-green-600 transition-colors">
                  Reconcile
                </button>
                <button class="px-3 py-1.5 bg-red-500 text-white text-sm rounded-md hover:bg-red-600 transition-colors">
                  Unmatch
                </button>
              </div>

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
                          <span class="text-gray-500">{{ transaction.statement_date }}</span>
                          <div>
                            <span v-if="transaction.dr_amount" class="text-red-500 mr-2">+{{ transaction.dr_amount }}</span>
                            <span v-if="transaction.cr_amount" class="text-green-500">-{{ transaction.cr_amount }}</span>
                          </div>
                        </div>
                        <div class="text-gray-600 truncate">{{ transaction.description }}</div>
                      </div>
                    </div>

                  </div>
                  <div class="px-4 py-2 text-right">
                    <span :class="Number(calculateTotal(data.statementTransactions)) < 0 ? 'text-green-500' : 'text-red-500'">{{ calculateTotal(data.statementTransactions) }}</span>
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
                        <!-- <div class="flex items-center justify-between">
                          <span class="text-sm text-gray-600">{{ transaction.date }}</span>
                          <div class="flex items-center space-x-2">
                            <span v-if="transaction.dr_amount" class="text-green-600 font-medium text-sm">
                              +{{ transaction.dr_amount }}
                            </span>
                            <span v-if="transaction.cr_amount" class="text-red-600 font-medium text-sm">
                              -{{ transaction.cr_amount }}
                            </span>
                          </div>
                        </div> -->

                        <div class="text-xs">
                          <!-- Add date too -->
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
</style>
