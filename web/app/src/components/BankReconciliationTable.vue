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
  return dr_amount - cr_amount
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


</script>
<template>
  <div>
    <!-- Unmatched section -->
    <div class="grid grid-cols-2 gap-10">
      <div class="border p-5 bg-gray-100 rounded-lg shadow-md">
        <div class="grid grid-cols-2 gap-6">

          <!-- Unmatched Statement Transactions -->
          <div class="p-4 bg-white rounded-lg shadow-sm border">
            <div class="text-lg font-semibold text-blue-600 mb-3">Unmatched Statement Transactions</div>
            <div v-for="data in unmatchedStatementTransactions" :key="data.id" class="border-b py-2">
              <div class="flex justify-between items-center mb-1">
                <div class="text-gray-700">Date:</div>
                <div class="font-medium">{{ data.statement_date }}</div>
              </div>
              <div class="flex justify-between items-center mb-1">
                <div class="text-gray-700">Debit Amount:</div>
                <div class="font-medium text-red-500">{{ data.dr_amount }}</div>
              </div>
              <div class="flex justify-between items-center mb-1">
                <div class="text-gray-700">Credit Amount:</div>
                <div class="font-medium text-green-500">{{ data.cr_amount }}</div>
              </div>
              <div class="flex justify-between items-center">
                <div class="text-gray-700">Balance:</div>
                <div class="font-medium text-purple-600">{{ data.balance }}</div>
              </div>
            </div>
          </div>

          <!-- Unmatched System Transactions -->
          <div class="p-4 bg-white rounded-lg shadow-sm border">
            <div class="text-lg font-semibold text-green-600 mb-3">Unmatched System Transactions</div>
            <div v-for="data in unmatchedSystemTransactions" :key="data.id" class="border-b py-2">
              <div class="flex justify-between items-center mb-1">
                <div class="text-gray-700">Id:</div>
                <div class="font-medium">{{ data.id }}</div>
              </div>
              <div class="flex justify-between items-center mb-1">
                <div class="text-gray-700">Date:</div>
                <div class="font-medium">{{ data.date }}</div>
              </div>
              <div class="flex justify-between items-center mb-1">
                <div class="text-gray-700">Debit Amount:</div>
                <div class="font-medium text-red-500">{{ data.dr_amount }}</div>
              </div>
              <div class="flex justify-between items-center mb-1">
                <div class="text-gray-700">Credit Amount:</div>
                <div class="font-medium text-green-500">{{ data.cr_amount }}</div>
              </div>
              <!-- <div class="flex justify-between items-center">
                <div class="text-gray-700">Balance:</div>
                <div class="font-medium text-purple-600">{{ data.balance }}</div>
              </div> -->
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
                    <div class="divide-y text-sm">
                      <div v-for="transaction in data.statementTransactions" :key="transaction.id" class="px-4 py-2.5">
                        <div class="flex justify-between mb-1">
                          <span class="text-gray-500">{{ transaction.statement_date }}</span>
                          <div>
                            <span v-if="transaction.dr_amount" class="text-red-500 mr-2">+{{ transaction.dr_amount }}</span>
                            <span v-if="transaction.cr_amount" class="text-green-500">-{{ transaction.cr_amount }}</span>
                          </div>
                        </div>
                        <div class="text-gray-600 text-xs truncate">{{ transaction.description }}</div>
                      </div>
                    </div>

                  </div>
                  <div class="px-4 py-2 text-right">
                    <span :class="calculateTotal(data.statementTransactions) < 0 ? 'text-green-500' : 'text-red-500'">{{ calculateTotal(data.statementTransactions) }}</span>
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
                      <div v-for="transaction in data.systemTransactions" :key="transaction.id" class="px-4 py-2.5">
                        <div class="flex justify-between mb-1">
                          <span class="text-gray-500">{{ transaction.date }}</span>
                          <div>
                            <span v-if="transaction.dr_amount" class="text-green-500 mr-2">+{{ transaction.dr_amount }}</span>
                            <span v-if="transaction.cr_amount" class="text-red-500">-{{ transaction.cr_amount }}</span>
                          </div>
                        </div>
                        <div class="text-gray-600 text-xs">{{ transaction.id }}</div>
                      </div>
                    </div>
                  </div>
                  <div class="px-4 py-2 text-right">
                    <span :class="calculateTotal(data.systemTransactions) < 0 ? 'text-red-500' : 'text-green-500'">{{ calculateTotal(data.systemTransactions) }}</span>
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
