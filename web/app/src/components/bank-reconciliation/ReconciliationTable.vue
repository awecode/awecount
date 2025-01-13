<script setup lang="ts">
import type { Ref } from 'vue'
import checkPermissions from 'src/composables/checkPermissions'
import { getPermissionFromSourceType, getVoucherUrl } from 'src/composables/getVoucherUrlAndPermissions'
import ChequeIssueForm from 'src/pages/bank/cheque-issue/ChequeIssueForm.vue'
import FundTransferForm from 'src/pages/bank/fund-transfer/FundTransferForm.vue'

interface AccountDetails {
  ledger_id: number
  id: number
  name: string
  account_number: string
  cheque_no: string
}
const props = defineProps({
  acceptableDifference: {
    type: Number,
    default: 0.01,
  },
  adjustmentThreshold: {
    type: Number,
    default: 1,
  },
  startDate: {
    type: String,
    required: true,
  },
  endDate: {
    type: String,
    required: true,
  },
  accountDetails: {
    type: Object as () => AccountDetails,
    required: true,
  },
})

const $q = useQuasar()

interface SystemTransactionData {
  id: number
  date: string
  dr_amount: string | null
  cr_amount: string | null
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
  dr_amount: string | null
  cr_amount: string | null
  balance: string
  description: string
  transaction_ids: number[]
}

interface StatementResponse {
  results: StatementTransactionData[]
  pagination: {
    page: number
    pages: number
    count: number
  }
}

interface SystemResponse {
  results: SystemTransactionData[]
  pagination: {
    page: number
    pages: number
    count: number
  }
}

const statementResponse: Ref<StatementResponse> = ref({
  results: [],
  pagination: {
    page: 1,
    pages: 1,
    count: 0,
  },
})

const systemResponse: Ref<SystemResponse> = ref({
  results: [],
  pagination: {
    page: 1,
    pages: 1,
    count: 0,
  },
})

const hasNoMatches = ref(false)

const statementSearchBy = ref('')
const systemSearchBy = ref('')
const statementSortBy = ref('date')
const systemSortBy = ref('date')
const statementSortDir = ref('asc')
const systemSortDir = ref('asc')
const statementPage = ref(1)
const systemPage = ref(1)
const bankScrollSection = ref()
const systemScrollSection = ref()
const isFundTransferModalOpen = ref(false)
const isChequeIssueModalOpen = ref(false)

const fetchUnmatchedBankTransactions = async () => {
  console.log('Start_date:', props.startDate)
  console.log('End_date:', props.endDate)
  console.log('Account_id:', props.accountDetails.ledger_id)
  if (!props.startDate || !props.endDate || !props.accountDetails.ledger_id) {
    return
  }
  await useApi(`v1/bank-reconciliation/unreconciled-bank-transactions/?start_date=${props.startDate}&end_date=${props.endDate}&account_id=${props.accountDetails.ledger_id}&search=${statementSearchBy.value}&sort_by=${statementSortBy.value}&sort_dir=${statementSortDir.value}&page=${statementPage.value}`)
    .then((response) => {
      if (response.pagination.page === 1) {
        statementResponse.value.results = response.results
      } else {
        statementResponse.value.results = [
          ...statementResponse.value.results,
          ...response.results.filter((result: StatementTransactionData) => {
            return !statementResponse.value.results.some(r => r.id === result.id)
          }),
        ]
      }
      statementResponse.value.pagination = response.pagination
      if (statementResponse.value.pagination.page < statementResponse.value.pagination.pages) {
        bankScrollSection.value?.resume()
      }
    })
    .catch((error) => {
      console.log(error)
      statementResponse.value.results = []
    })
    .catch((error) => {
      console.log(error)
      statementResponse.value.results = []
    })
}

fetchUnmatchedBankTransactions()

const fetchUnmatchedSystemTransactions = async () => {
  if (!props.startDate || !props.endDate || !props.accountDetails.ledger_id) {
    return
  }
  await useApi(`v1/bank-reconciliation/unreconciled-system-transactions/?start_date=${props.startDate}&end_date=${props.endDate}&account_id=${props.accountDetails.ledger_id}&search=${systemSearchBy.value}&sort_by=${systemSortBy.value}&sort_dir=${systemSortDir.value}&page=${systemPage.value}`)
    .then((response) => {
      // systemResponse.value.results = []
      if (response.pagination.page === 1) {
        systemResponse.value.results = response.results
      } else {
        systemResponse.value.results = [
          ...systemResponse.value.results,
          ...response.results.filter((result: SystemTransactionData) => {
            return !systemResponse.value.results.some(r => r.id === result.id)
          }),
        ]
      }
      systemResponse.value.pagination = response.pagination
      if (systemResponse.value.pagination.page < systemResponse.value.pagination.pages) {
        systemScrollSection.value?.resume()
      }
    })
    .catch((error) => {
      console.log(error)
      systemResponse.value.results = []
    })
    .catch((error) => {
      console.log(error)
      systemResponse.value.results = []
    })
}

fetchUnmatchedSystemTransactions()

const openSalesInvoiceModal = ref(false)

const sortBy = [
  {
    label: 'Date',
    value: 'date',
  },
  {
    label: 'Dr Amount',
    value: 'dr_amount',
  },
  {
    label: 'Cr Amount',
    value: 'cr_amount',
  },
]

const calculateTotal = (transactions: SystemTransactionData[] | StatementTransactionData[], forStatement = false) => {
  let cr_amount = 0
  let dr_amount = 0
  for (const transaction of transactions) {
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

const calculateTotalFromCounterparts = (counterparts: { dr_amount: string | null, cr_amount: string | null }[]) => {
  let cr_amount = 0
  let dr_amount = 0
  for (const counterpart of counterparts) {
    if (counterpart.cr_amount) {
      cr_amount += Number(counterpart.cr_amount)
    }
    if (counterpart.dr_amount) {
      dr_amount += Number(counterpart.dr_amount)
    }
  }
  return (dr_amount - cr_amount).toFixed(2)
}

const filterSources = (systemTransactions: SystemTransactionData[]): { source_id: number, url: string, source_type: string }[] => {
  const sourceMap = new Map<number, { source_id: number, url: string, source_type: string }>()

  systemTransactions.forEach((transaction: SystemTransactionData) => {
    if (transaction.source_id) {
      // check permission
      if (checkPermissions(getPermissionFromSourceType(transaction.source_type))) {
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
const allStatementSelected = computed(() => selectedStatementTransactions.value.length === statementResponse.value.results.length)

const allSystemSelected = computed(() => selectedSystemTransactions.value.length === systemResponse.value.results.length)

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
    selectedStatementTransactions.value = [...statementResponse.value.results]
  }
}

const toggleAllSystemTransactions = () => {
  if (allSystemSelected.value) {
    selectedSystemTransactions.value = []
  } else {
    selectedSystemTransactions.value = [...systemResponse.value.results]
  }
}

// Check if a specific transaction is selected
const isStatementTransactionSelected = (transaction: StatementTransactionData) => selectedStatementTransactions.value.some(t => t.id === transaction.id)

const isSystemTransactionSelected = (transaction: SystemTransactionData) => selectedSystemTransactions.value.some(t => t.id === transaction.id)

const canReconcile = computed(
  () => {
    return selectedStatementTransactions.value.length > 0 && selectedSystemTransactions.value.length > 0 && Math.abs(Number(calculateTotal(selectedStatementTransactions.value, true)) - Number(calculateTotal(selectedSystemTransactions.value))) < props.acceptableDifference
  },
  // also total amount matches
)

const unselectAll = () => {
  selectedStatementTransactions.value = []
  selectedSystemTransactions.value = []
}

const reconcile = () => {
  if (selectedStatementTransactions.value.length > 0 || selectedSystemTransactions.value.length > 0) {
    const endpoint = canReconcile.value ? 'v1/bank-reconciliation/reconcile-transactions/' : 'v1/bank-reconciliation/reconcile-with-adjustment/'
    useApi(endpoint, {
      method: 'POST',
      body: {
        statement_ids: selectedStatementTransactions.value.map(t => t.id),
        transaction_ids: selectedSystemTransactions.value.map(t => t.id),
        narration: 'Test Narration',
      },
    })
      .then(() => {
        // remove from both unmatched lists
        selectedStatementTransactions.value.forEach((t) => {
          const index = statementResponse.value.results.findIndex(ut => ut === t)
          if (index > -1) {
            statementResponse.value.results.splice(index, 1)
          }
        })
        selectedSystemTransactions.value.forEach((t) => {
          const index = systemResponse.value.results.findIndex(ut => ut === t)
          if (index > -1) {
            systemResponse.value.results.splice(index, 1)
          }
        })
        unselectAll()
        $q.notify({
          color: 'green-6',
          message: 'Transactions reconciled successfully',
          icon: 'check_circle',
          position: 'top-right',
        })
      })
      .catch((error) => {
        console.log(error)
        $q.notify({
          color: 'red-6',
          message: 'Failed to reconcile transactions',
          icon: 'error',
          position: 'top-right',
        })
      })
  }
}

const loadMoreSystemTransactions = async (index: number, done: any) => {
  if (systemPage.value < systemResponse.value.pagination.pages) {
    systemPage.value++
    await fetchUnmatchedSystemTransactions()
  } else {
    systemScrollSection.value?.stop()
  }
  done()
}

const loadMoreStatementTransactions = async (index: number, done: any) => {
  if (statementPage.value < statementResponse.value.pagination.pages) {
    statementPage.value++
    await fetchUnmatchedBankTransactions()
  } else {
    bankScrollSection.value?.stop()
  }
  done()
}

const unmatchTransactions = (transaction: { statement_transactions: StatementTransactionData[], system_transactions: SystemTransactionData[] }) => {
  statementResponse.value.results.unshift(
    ...transaction.statement_transactions.map((t) => {
      return {
        ...t,
        transaction_ids: [],
      }
    }),
  )
  systemResponse.value.results.unshift(...transaction.system_transactions)
}

const removeBankTransactions = (transaction: StatementTransactionData[]) => {
  transaction.forEach((t) => {
    const index = statementResponse.value.results.findIndex(ut => ut.id === t.id)
    if (index > -1) {
      statementResponse.value.results.splice(index, 1)
    }
    const selectedTransactionIndex = selectedStatementTransactions.value.findIndex(ut => ut.id === t.id)
    if (selectedTransactionIndex > -1) {
      selectedStatementTransactions.value.splice(selectedTransactionIndex, 1)
    }
  })
}

const isAllStatementCredit = computed(() => {
  return selectedStatementTransactions.value.every(t => t.cr_amount)
})

const isAllStatementDebit = computed(() => {
  return selectedStatementTransactions.value.every(t => t.dr_amount)
})

const findLatestDate = (transactions: SystemTransactionData[] | StatementTransactionData[]) => {
  let latestDate = ''
  transactions.forEach((transaction) => {
    if (transaction.date > latestDate) {
      latestDate = transaction.date
    }
  })
  return latestDate
}

const onFundTransferChequeIssueSuccess = () => {
  statementResponse.value.results = statementResponse.value.results.filter((t) => {
    return !selectedStatementTransactions.value.some(st => st.id === t.id)
  })
  unselectAll()
  isFundTransferModalOpen.value = false
  isChequeIssueModalOpen.value = false
}
</script>

<template>
  <div class="max-h-[800px]">
    <!-- Unmatched section -->
    <div class="grid gap-10" :class="!hasNoMatches ? 'grid-cols-2' : ''">
      <div class="border p-5 bg-gray-100 rounded-lg shadow-md">
        <div class="bg-gray-100 p-4 pt-0 rounded-lg">
          <div class="flex space-x-3 w-fit ml-auto">
            <div v-if="selectedStatementTransactions.length && !selectedSystemTransactions.length && (isAllStatementCredit || isAllStatementDebit)">
              <div v-if="isAllStatementCredit">
                <button v-if="selectedStatementTransactions.length && !selectedSystemTransactions.length" class="px-4 py-2 bg-green-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm cursor-pointer" @click="openSalesInvoiceModal = true">
                  Find Sales Invoices
                </button>
              </div>
              <div v-else>
                <button class="px-4 py-2 bg-yellow-200 cursor-pointer text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm mr-3" @click="isFundTransferModalOpen = true">
                  Fund Transfer
                </button>
                <button class="px-4 cursor-pointer py-2 bg-yellow-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm" @click="isChequeIssueModalOpen = true">
                  Cheque Issue
                </button>
              </div>
            </div>
            <button class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors cursor-pointer text-sm" @click="unselectAll">
              Unselect All
            </button>
            <button v-if="canReconcile" class="px-4 cursor-pointer py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm" @click="reconcile">
              Reconcile
            </button>
            <button v-else-if="selectedStatementTransactions.length && selectedSystemTransactions.length && Math.abs(Number(calculateTotal(selectedStatementTransactions, true)) - Number(calculateTotal(selectedSystemTransactions))) <= props.adjustmentThreshold" class="px-4 py-2 bg-blue-500 cursor-pointer text-white rounded-md hover:bg-blue-600 transition-colors text-sm" @click="reconcile">
              Reconcile with Adjustment
            </button>
            <button v-else disabled class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed">
              Reconcile
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
              <div class="font-medium" :class="Math.abs(Number(calculateTotal(selectedStatementTransactions, true)) - Number(calculateTotal(selectedSystemTransactions))) > props.acceptableDifference ? 'text-red-600' : 'text-green-600'">
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
              <div class="flex space-x-2 text-gray-700">
                <q-select
                  v-model="statementSortBy"
                  dense
                  emit-value
                  outlined
                  class="w-32"
                  label="Sort by"
                  option-label="label"
                  option-value="value"
                  :options="sortBy"
                  @update:model-value="(statementPage = 1), fetchUnmatchedBankTransactions()"
                />
                <div class="flex items-center pb-2 cursor-pointer">
                  <svg
                    height="20"
                    viewBox="0 0 12 20"
                    width="10"
                    xmlns="http://www.w3.org/2000/svg"
                    :class="statementSortDir === 'asc' ? 'transform rotate-180' : ''"
                    @click="(statementSortDir = statementSortDir === 'asc' ? 'desc' : 'asc'), (statementPage = 1), fetchUnmatchedBankTransactions()"
                  >
                    <g
                      fill="none"
                      stroke="currentColor"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                    >
                      <path d="M6 3l0 17.5" stroke-dasharray="20" stroke-dashoffset="20">
                        <animate
                          attributeName="stroke-dashoffset"
                          dur="0.2s"
                          fill="freeze"
                          values="20;0"
                        />
                      </path>
                      <path d="M6 21l5 -5M6 21l-5 -5" stroke-dasharray="12" stroke-dashoffset="12">
                        <animate
                          attributeName="stroke-dashoffset"
                          begin="0.2s"
                          dur="0.2s"
                          fill="freeze"
                          values="12;0"
                        />
                      </path>
                    </g>
                  </svg>
                </div>
              </div>
              <!-- Arrow icon to show asc and desc -->
              <q-input
                v-model="statementSearchBy"
                dense
                outlined
                class="grow mb-2"
                placeholder="Search..."
                :debounce="500"
                @update:model-value="(statementPage = 1), fetchUnmatchedBankTransactions()"
              />
            </div>
            <div class="bg-white rounded-lg shadow-sm border overflow-hidden">
              <div class="px-4 py-3 border-b bg-blue-50">
                <h3 class="text-lg my-0 font-semibold text-blue-600">
                  Unmatched Statement Transactions
                  <span class="text-sm text-blue-500 ml-2">({{ statementResponse.results.length }})</span>
                </h3>
                <div class="flex items-center justify-between mt-2">
                  <div>
                    <input
                      class="px-4 h-4 w-4 text-blue-600 rounded"
                      type="checkbox"
                      :checked="allStatementSelected"
                      @change="toggleAllStatementTransactions"
                    />
                    <span class="ml-2 text-sm text-gray-600">Select All</span>
                  </div>
                  <!-- <div>
                    <span class="font-medium" :class="Number(calculateTotal(filteredUnmatchedStatementTransactions, true)) < 0 ? 'text-red-500' : 'text-green-500'">{{
                      calculateTotal(filteredUnmatchedStatementTransactions, true)
                      }}</span>
                  </div> -->
                </div>
              </div>

              <div v-if="statementResponse.results.length" class="divide-y overflow-y-auto text-xs bank-section max-h-[500px]">
                <q-infinite-scroll
                  ref="bankScrollSection"
                  scroll-target=".bank-section"
                  :offset="250"
                  @load="loadMoreStatementTransactions"
                >
                  <div
                    v-for="data in statementResponse.results"
                    :key="data.id"
                    class="px-4 hover:bg-gray-50 flex flex-nowrap items-center space-x-3 border-b cursor-pointer"
                    @click="toggleStatementTransaction(data)"
                  >
                    <input class="px-4 h-4 w-4 text-green-600 rounded" type="checkbox" :checked="isStatementTransactionSelected(data)" />
                    <div :key="data.id" class="py-3 pl-2 pr-0 border-gray-200 hover:bg-gray-50 transition-colors duration-200 relative grow">
                      <div class="flex justify-between mb-1">
                        <span class="text-gray-500">{{ data.date }}</span>
                        <div class="font-medium">
                          <span v-if="data.dr_amount" class="text-red-500">-{{ data.dr_amount }}</span>
                          <span v-if="data.cr_amount" class="text-green-500">+{{ data.cr_amount }}</span>
                        </div>
                      </div>
                      <div class="text-gray-600">
                        {{ data.description }}
                      </div>
                    </div>
                  </div>
                  <template #loading>
                    <div class="row justify-center q-my-md">
                      <q-spinner-dots color="primary" size="40px" />
                    </div>
                  </template>
                </q-infinite-scroll>
              </div>
            </div>
          </div>
          <!-- --------------------------------------------------------------                  Unmatched System Transactions                      -------------------------------------------------------------------------------- -->

          <div>
            <div class="flex gap-4">
              <div class="flex space-x-2">
                <q-select
                  v-model="systemSortBy"
                  dense
                  emit-value
                  outlined
                  class="w-32"
                  label="Sort by"
                  option-label="label"
                  option-value="value"
                  :options="sortBy"
                  @update:model-value="(systemPage = 1), fetchUnmatchedSystemTransactions()"
                />
                <div class="flex items-center pb-2 cursor-pointer text-gray-700">
                  <svg
                    height="20"
                    viewBox="0 0 12 20"
                    width="10"
                    xmlns="http://www.w3.org/2000/svg"
                    :class="systemSortDir === 'asc' ? 'transform rotate-180' : ''"
                    @click="(systemSortDir = systemSortDir === 'asc' ? 'desc' : 'asc'), (systemPage = 1), fetchUnmatchedSystemTransactions()"
                  >
                    <g
                      fill="none"
                      stroke="currentColor"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                    >
                      <path d="M6 3l0 17.5" stroke-dasharray="20" stroke-dashoffset="20">
                        <animate
                          attributeName="stroke-dashoffset"
                          dur="0.2s"
                          fill="freeze"
                          values="20;0"
                        />
                      </path>
                      <path d="M6 21l5 -5M6 21l-5 -5" stroke-dasharray="12" stroke-dashoffset="12">
                        <animate
                          attributeName="stroke-dashoffset"
                          begin="0.2s"
                          dur="0.2s"
                          fill="freeze"
                          values="12;0"
                        />
                      </path>
                    </g>
                  </svg>
                </div>
              </div>

              <q-input
                v-model="systemSearchBy"
                dense
                outlined
                class="grow mb-2"
                placeholder="Search..."
                :debounce="500"
                @update:model-value="(systemPage = 1), fetchUnmatchedSystemTransactions()"
              />
            </div>
            <div class="bg-white rounded-lg shadow-sm border overflow-hidden">
              <div class="px-4 py-3 border-b bg-green-50">
                <h3 class="text-lg my-0 font-semibold text-green-600">
                  Unmatched System Transactions
                  <span class="text-sm text-green-500 ml-2">({{ systemResponse.results.length }})</span>
                </h3>
                <div class="flex items-center justify-between mt-2">
                  <div class="flex items-centers">
                    <input
                      class="px-4 h-4 w-4 text-green-600 rounded"
                      type="checkbox"
                      :checked="allSystemSelected"
                      @change="toggleAllSystemTransactions"
                    />
                    <span class="ml-2 text-sm text-gray-600">Select All</span>
                  </div>
                  <!-- <div>
                    <span class="font-medium" :class="Number(calculateTotal(systemResponse.results)) < 0 ? 'text-red-500' : 'text-green-500'">{{
                      calculateTotal(systemResponse.results)
                    }}</span>
                  </div> -->
                </div>
              </div>

              <div v-if="systemResponse.results.length" class="divide-y overflow-y-auto system-section max-h-[500px]">
                <q-infinite-scroll
                  ref="systemScrollSection"
                  scroll-target=".system-section"
                  :offset="250"
                  @load="loadMoreSystemTransactions"
                >
                  <div
                    v-for="data in systemResponse.results"
                    :key="data.id"
                    class="flex items-center border-b px-3 py-3 hover:bg-gray-50 transition-colors duration-200 cursor-pointer"
                    @click="toggleSystemTransaction(data)"
                  >
                    <input class="h-5 w-5 mr-3 text-green-600 rounded focus:ring-2 focus:ring-green-500" type="checkbox" :checked="isSystemTransactionSelected(data)" />

                    <div class="flex-grow min-w-0">
                      <!-- Transaction Header -->
                      <div class="flex justify-between items-center mb-2">
                        <span class="text-xs text-gray-500">{{ data.date }}</span>

                        <router-link
                          v-if="data.source_type && data.source_id && checkPermissions(getPermissionFromSourceType(data.source_type))"
                          class="text-blue-800 text-xs hover:underline"
                          target="_blank"
                          :to="getVoucherUrl(data) as string"
                          @click.stop
                        >
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
                            <span v-if="counterpart.dr_amount" class="text-red-600 font-medium">-{{ counterpart.dr_amount }}</span>
                            <span v-if="counterpart.cr_amount" class="text-green-600 font-medium">+{{ counterpart.cr_amount }}</span>
                          </div>
                        </div>
                      </div>

                      <!-- Total for Multiple Counterparts -->
                      <div v-if="data.counterpart_accounts.length > 1" class="border-t text-right text-xs w-fit ml-auto">
                        <span v-if="data.dr_amount" class="text-green-500 font-semibold">+{{ data.dr_amount }}</span>
                        <span v-if="data.cr_amount" class="text-red-500 font-semibold ml-2">-{{ data.cr_amount }}</span>
                      </div>
                    </div>
                  </div>
                  <template #loading>
                    <div class="row justify-center q-my-md">
                      <q-spinner-dots color="primary" size="40px" />
                    </div>
                  </template>
                </q-infinite-scroll>
              </div>
            </div>
          </div>
        </div>
      </div>

      <MatchedTransactions
        :account-id="accountDetails.ledger_id"
        :calculate-total="calculateTotal"
        :calculate-total-from-counterparts="calculateTotalFromCounterparts"
        :end-date="endDate"
        :filter-sources="filterSources"
        :start-date="startDate"
        @has-no-matches="hasNoMatches = true"
        @unmatch-transactions="unmatchTransactions"
      />
    </div>
  </div>
  <ReconciliationSalesInvoicesModal
    v-if="openSalesInvoiceModal"
    v-model="openSalesInvoiceModal"
    :acceptable-difference="acceptableDifference"
    :adjustment-threshold="adjustmentThreshold"
    :end-date="endDate"
    :start-date="startDate"
    :statement-transactions="selectedStatementTransactions"
    @remove-bank-transactions="removeBankTransactions"
  />

  <q-dialog v-model="isFundTransferModalOpen">
    <div class="min-w-[900px]">
      <FundTransferForm
        class="w-full"
        endpoint="v1/bank-reconciliation/reconcile-transactions-with-funds-transfer/"
        :amount="Math.abs(Number(calculateTotal(selectedStatementTransactions, true)))"
        :date="findLatestDate(selectedStatementTransactions)"
        :from-account="{
          id: accountDetails.ledger_id,
          name: accountDetails.name,
        }"
        :is-modal="true"
        :statement-ids="selectedStatementTransactions.map((t) => t.id)"
        @modal-signal="onFundTransferChequeIssueSuccess"
      />
      />
    </div>
  </q-dialog>

  <q-dialog v-model="isChequeIssueModalOpen">
    <div class="min-w-[900px]">
      <ChequeIssueForm
        class="w-full"
        endpoint="v1/bank-reconciliation/reconcile-transactions-with-cheque-issue/"
        :amount="Math.abs(Number(calculateTotal(selectedStatementTransactions, true)))"
        :bank-account="{
          id: accountDetails.id,
          name: accountDetails.name,
          account_number: accountDetails.account_number,
          cheque_no: accountDetails.cheque_no,
        }"
        :date="findLatestDate(selectedStatementTransactions)"
        :is-modal="true"
        :statement-ids="selectedStatementTransactions.map((t) => t.id)"
        @modal-signal="onFundTransferChequeIssueSuccess"
      />
    </div>
  </q-dialog>
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
