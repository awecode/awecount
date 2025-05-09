<script setup lang="ts">
import type { Ref } from 'vue'
import checkPermissions from 'src/composables/checkPermissions'
import { useRoute } from 'vue-router'

const props = defineProps({
  statementTransactions: {
    type: Array<StatementTransactionData>,
    required: true,
  },
  startDate: {
    type: String,
    required: true,
  },
  endDate: {
    type: String,
    required: true,
  },
  modelValue: {
    type: Boolean,
    default: () => null,
  },
  acceptableDifference: {
    type: Number,
    default: 0.01,
  },
  adjustmentThreshold: {
    type: Number,
    default: 1,
  },
})

const emit = defineEmits(['update:modelValue', 'removeBankTransactions'])

const $q = useQuasar()

interface StatementTransactionData {
  id: number
  date: string
  dr_amount: string | null
  cr_amount: string | null
  balance: string
  description: string
  transaction_ids: number[]
}

interface Invoice {
  id: number
  date: string
  party_name: string | null
  total_amount: number
  customer_name: string | null
  remarks: string | null
  selected: boolean
}

const prompt = ref(props.modelValue)

const sortOptions = ref([
  {
    label: 'Date',
    value: 'date',
  },
  {
    label: 'Total Amount',
    value: 'total_amount',
  },
])

const sortBy = ref('date')
const sortDir = ref('desc')
const infiniteScroll = ref()
const tdsAndRemarks = ref(false)
const tds = ref(null)
const remarks = ref(null)

const closeTDSAndRemarks = () => {
  tds.value = null
  remarks.value = null
  tdsAndRemarks.value = false
}

interface SalesInvoiceResponse {
  results: Invoice[]
  pagination: {
    page: number
    pages: number
    count: number
  }
}

const response: Ref<SalesInvoiceResponse> = ref({
  results: [],
  pagination: {
    page: 1,
    pages: 1,
    count: 0,
  },
})

const search = ref('')
const filterStartDate = ref(props.startDate)
const filterEndDate = ref(props.endDate)
const page = ref(1)

const route = useRoute()

const searchInvoice = async () => {
  await useApi(`/api/company/${route.params.company}/bank-reconciliation/sales-vouchers/?start_date=${filterStartDate.value}&end_date=${filterEndDate.value}&search=${search.value}&sort_by=${sortBy.value}&sort_dir=${sortDir.value}&page=${page.value}`).then((responseData: SalesInvoiceResponse) => {
    if (responseData.pagination.page === 1) {
      response.value.results = responseData.results.map((invoice) => {
        return {
          ...invoice,
          selected: false,
        }
      })
    } else {
      response.value.results = [
        ...response.value.results,
        ...responseData.results.map((invoice) => {
          return {
            ...invoice,
            selected: false,
          }
        }),
      ]
    }
    response.value.pagination = responseData.pagination
    // if has more pages reset infinite scroll
    if (response.value.pagination.page < response.value.pagination.pages) {
      infiniteScroll.value?.reset()
      infiniteScroll.value?.resume()
    }
  })
}

searchInvoice()

const allStatementTransactions = ref(
  props.statementTransactions.map((transaction) => {
    return {
      ...transaction,
      selected: false,
    }
  }),
)

// get total amount of selected statement transactions
const allStatementSelected = computed(() => {
  return selectedStatementTransactions.value.length === allStatementTransactions.value.length
})

const selectedStatementTransactions: Ref<StatementTransactionData[]> = ref(props.statementTransactions)
const selectedInvoiceTransactions: Ref<Invoice[]> = ref([])

const toggleAllStatementTransactions = () => {
  if (allStatementSelected.value) {
    allStatementTransactions.value = allStatementTransactions.value.map((transaction) => {
      return {
        ...transaction,
        selected: false,
      }
    })
    selectedStatementTransactions.value = []
  } else {
    allStatementTransactions.value = allStatementTransactions.value.map((transaction) => {
      return {
        ...transaction,
        selected: true,
      }
    })
    selectedStatementTransactions.value = [...allStatementTransactions.value]
  }
}

const isStatementTransactionSelected = (transaction: StatementTransactionData) => {
  return selectedStatementTransactions.value.some(selectedTransaction => selectedTransaction.id === transaction.id)
}
const toggleStatementTransaction = (transaction: StatementTransactionData) => {
  if (isStatementTransactionSelected(transaction)) {
    selectedStatementTransactions.value = selectedStatementTransactions.value.filter(selectedTransaction => selectedTransaction.id !== transaction.id)
  } else {
    selectedStatementTransactions.value = [...selectedStatementTransactions.value, transaction]
  }
}

const isInvoiceSelected = (transaction: Invoice) => {
  return selectedInvoiceTransactions.value.some(selectedTransaction => selectedTransaction.id === transaction.id)
}

const toggleInvoiceSelection = (transaction: Invoice) => {
  if (isInvoiceSelected(transaction)) {
    selectedInvoiceTransactions.value = selectedInvoiceTransactions.value.filter(selectedTransaction => selectedTransaction.id !== transaction.id)
  } else {
    selectedInvoiceTransactions.value = [...selectedInvoiceTransactions.value, transaction]
  }
}

const allInvoiceSelected = computed(() => {
  return selectedInvoiceTransactions.value.length === response.value.results.length
})

const toggleAllInvoiceTransactions = () => {
  if (allInvoiceSelected.value) {
    response.value.results = response.value.results.map((invoice) => {
      return {
        ...invoice,
        selected: false,
      }
    })
    selectedInvoiceTransactions.value = []
  } else {
    response.value.results = response.value.results.map((invoice) => {
      return {
        ...invoice,
        selected: true,
      }
    })
    selectedInvoiceTransactions.value = [...response.value.results]
  }
}

const updatePrompt = (value: boolean) => {
  emit('update:modelValue', value)
}

const reconcile = () => {
  if (selectedStatementTransactions.value.length > 0 || selectedInvoiceTransactions.value.length > 0) {
    const endpoint = canReconcile.value ? `/api/company/${route.params.company}/bank-reconciliation/reconcile-transactions-with-sales-vouchers/` : `/api/company/${route.params.company}/bank-reconciliation/reconcile-transactions-with-sales-vouchers-and-adjustment/`
    useApi(endpoint, {
      method: 'POST',
      body: {
        statement_ids: selectedStatementTransactions.value.map(t => t.id),
        invoice_ids: selectedInvoiceTransactions.value.map(t => t.id),
        remarks: remarks.value,
        tds_amount: tds.value,
      },
    })
      .then(() => {
        allStatementTransactions.value = allStatementTransactions.value.filter((transaction) => {
          return !selectedStatementTransactions.value.some(selectedTransaction => selectedTransaction.id === transaction.id)
        })
        response.value.results = response.value.results.filter((invoice) => {
          return !selectedInvoiceTransactions.value.some(selectedTransaction => selectedTransaction.id === invoice.id)
        })
        emit('removeBankTransactions', selectedStatementTransactions.value)
        unselectAll()
        closeTDSAndRemarks()
        if (allStatementTransactions.value.length === 0) {
          updatePrompt(false)
        }
        $q.notify({
          color: 'green-5',
          textColor: 'white',
          icon: 'mdi-check',
          message: 'Transactions reconciled successfully',
        })
      })
      .catch((error) => {
        console.log(error)
      })
  }
}

const unselectAll = () => {
  allStatementTransactions.value = allStatementTransactions.value.map((transaction) => {
    return {
      ...transaction,
      selected: false,
    }
  })
  selectedStatementTransactions.value = []
  response.value.results = response.value.results.map((invoice) => {
    return {
      ...invoice,
      selected: false,
    }
  })
  selectedInvoiceTransactions.value = []
}

const canReconcile = computed(() => {
  return calculateInvoiceTotal(selectedInvoiceTransactions.value) === Number(calculateStatementTotal(selectedStatementTransactions.value))
})

const calculateStatementTotal = (transactions: StatementTransactionData[]) => {
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
  return (cr_amount - dr_amount).toFixed(2)
}

const calculateInvoiceTotal = (transactions: Invoice[]) => {
  return transactions.reduce((total, transaction) => {
    return total + transaction.total_amount
  }, 0)
}

const loadSalesInvoice = async (index: number, done: any) => {
  console.log('loading')
  if (page.value < response.value.pagination.pages) {
    page.value += 1
    await searchInvoice()
  } else {
    infiniteScroll.value?.stop()
  }
  done()
}
</script>

<template>
  <q-dialog v-model="prompt" no-shake @update:model-value="updatePrompt">
    <q-card class="p-5 space-y-3 overflow-hidden" style="min-width: 1000px; height: 90vh">
      <div class="text-xl text-gray-700 font-bold">
        Find Sales Invoices
      </div>
      <div class="bg-gray-100 p-4 rounded-lg">
        <div class="flex space-x-3 w-fit ml-auto">
          <button class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm" @click="unselectAll">
            Unselect All
          </button>
          <button v-if="canReconcile" class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm" @click="tdsAndRemarks = true">
            Reconcile
          </button>
          <button v-else-if="selectedStatementTransactions.length && selectedInvoiceTransactions.length && Math.abs(Number(calculateStatementTotal(selectedStatementTransactions)) - Number(calculateInvoiceTotal(selectedInvoiceTransactions))) <= props.adjustmentThreshold" class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm" @click="tdsAndRemarks = true">
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
                {{ calculateStatementTotal(selectedStatementTransactions) }}
              </span>
            </div>
          </div>

          <!-- Show difference -->
          <div class="text-sm text-center flex flex-col justify-center space-y-1">
            <span class="font-semibold">Difference:</span>
            <div class="font-medium" :class="Math.abs(Number(calculateStatementTotal(selectedStatementTransactions)) - Number(calculateInvoiceTotal(selectedInvoiceTransactions))) > props.acceptableDifference ? 'text-red-600' : 'text-green-600'">
              {{ Math.abs(Number(calculateStatementTotal(selectedStatementTransactions)) - Number(calculateInvoiceTotal(selectedInvoiceTransactions))) }}
            </div>
          </div>

          <!-- System Transactions Summary -->
          <div class="space-y-1">
            <div class="flex items-center">
              <span class="text-lg font-semibold text-green-700">Sales Invoices</span>
              <span class="text-xs text-green-500 ml-2 bg-green-100 px-2 py-1 rounded-full">
                {{ selectedInvoiceTransactions.length }}
              </span>
            </div>
            <div class="text-sm text-gray-600">
              Total:
              <span class="font-medium text-green-600">
                {{ calculateInvoiceTotal(selectedInvoiceTransactions) }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div class="max-h-[65vh] bg-gray-100 h-full">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 pb-0 bg-gray-100">
          <div></div>
          <div class="flex gap-4 mb-2">
            <div class="flex space-x-2">
              <q-select
                v-model="sortBy"
                dense
                emit-value
                outlined
                class="w-32"
                label="Sort by"
                option-label="label"
                option-value="value"
                :options="sortOptions"
                @update:model-value="((page = 1), searchInvoice())"
              />
              <div class="flex items-center pb-2 cursor-pointer text-gray-700">
                <svg
                  height="20"
                  viewBox="0 0 12 20"
                  width="10"
                  xmlns="http://www.w3.org/2000/svg"
                  :class="sortDir === 'asc' ? 'transform rotate-180' : ''"
                  @click="((sortDir = sortDir === 'asc' ? 'desc' : 'asc'), (page = 1), searchInvoice())"
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
              v-model="search"
              dense
              outlined
              class="grow mb-2"
              placeholder="Search..."
              :debounce="500"
              @update:model-value="((page = 1), searchInvoice())"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 pt-0">
          <!-- Statement Transactions Column -->
          <div class="space-y-4">
            <div class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              <div class="bg-blue-50 px-6 py-4 border-b border-blue-100 flex items-center justify-between">
                <h3 class="text-xl my-0 font-bold text-blue-700 tracking-tight">
                  Statement Transactions
                </h3>
                <div class="flex items-center space-x-3">
                  <input
                    class="h-5 w-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 transition duration-200"
                    type="checkbox"
                    :checked="allStatementSelected"
                    @change="toggleAllStatementTransactions"
                  />
                  <span class="text-sm text-gray-600 font-medium">Select All</span>
                </div>
              </div>

              <div class="divide-y divide-gray-100 max-h-[calc(75vh-250px)] overflow-y-auto">
                <div v-for="data in allStatementTransactions" :key="data.id" class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150 flex flex-nowrap items-center space-x-4">
                  <input
                    class="h-5 w-5 text-green-600 rounded focus:ring-2 focus:ring-green-500"
                    type="checkbox"
                    :checked="isStatementTransactionSelected(data)"
                    @change="toggleStatementTransaction(data)"
                  />
                  <div class="flex-grow">
                    <div class="flex flex-nowrap justify-between items-center mb-1">
                      <span class="text-sm text-gray-500">{{ data.date }}</span>
                      <div class="font-semibold">
                        <span v-if="data.dr_amount" class="text-red-500">-{{ data.dr_amount }}</span>
                        <span v-if="data.cr_amount" class="text-green-500">+{{ data.cr_amount }}</span>
                      </div>
                    </div>
                    <p class="text-sm text-gray-700 break">
                      {{ data.description }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Unpaid Sales Invoices Column -->
          <div class="space-y-4">
            <div class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
              <div class="bg-green-50 px-6 py-4 border-b border-green-100 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <h3 class="text-xl my-0 font-bold text-green-700 tracking-tight">
                    Sales Invoices
                  </h3>
                  <span class="text-sm text-green-600 bg-green-100 px-2 py-0.5 rounded-full">
                    {{ response.results.length }}
                  </span>
                </div>
                <div class="flex items-center space-x-3">
                  <input
                    class="h-5 w-5 text-green-600 rounded focus:ring-2 focus:ring-green-500 transition duration-200"
                    type="checkbox"
                    :checked="allInvoiceSelected"
                    @change="toggleAllInvoiceTransactions"
                  />
                  <span class="text-sm text-gray-600 font-medium">Select All</span>
                </div>
              </div>

              <div v-if="response.results.length" class="divide-y divide-gray-100 overflow-y-auto max-h-[calc(75vh-250px)] sales-invoices">
                <q-infinite-scroll
                  ref="infiniteScroll"
                  scroll-target=".sales-invoices"
                  :offset="250"
                  @load="loadSalesInvoice"
                >
                  <div v-for="data in response.results" :key="data.id" class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150 flex flex-nowrap items-center space-x-4">
                    <input
                      class="h-5 w-5 text-green-600 rounded focus:ring-2 focus:ring-green-500"
                      type="checkbox"
                      :checked="isInvoiceSelected(data)"
                      @change="toggleInvoiceSelection(data)"
                    />
                    <div class="flex-grow">
                      <div class="flex justify-between items-center mb-1">
                        <span class="text-sm text-gray-500">{{ data.date }}</span>
                        <router-link
                          v-if="checkPermissions('sales.read')"
                          class="text-blue-600 text-xs hover:underline"
                          target="_blank"
                          :to="`/${$route.params.company}/sales/vouchers/${data.id}`"
                        >
                          Sales Invoice
                        </router-link>
                      </div>
                      <div class="flex justify-between items-center flex-nowrap">
                        <div class="text-sm text-gray-700 break pr-2">
                          {{ data.party_name || data.customer_name }}
                        </div>
                        <div class="text-green-500 font-semibold">
                          +{{ data.total_amount }}
                        </div>
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
    </q-card>
  </q-dialog>
  <q-dialog v-model="tdsAndRemarks">
    <q-card class="p-5" style="min-width: 650px">
      <q-input v-model="tds" dense label="TDS Amount" />
      <q-input
        v-model="remarks"
        dense
        class="my-5"
        label="Remarks"
      />
      <div class="flex justify-end space-x-3">
        <q-btn v-if="canReconcile" class="px-3 py-1.5 bg-green-500 text-white text-sm rounded-md hover:bg-green-600 transition-colors" @click="reconcile">
          Reconcile
        </q-btn>
        <q-btn v-else-if="selectedStatementTransactions.length && selectedInvoiceTransactions.length && Math.abs(Number(calculateStatementTotal(selectedStatementTransactions)) - Number(calculateInvoiceTotal(selectedInvoiceTransactions))) <= props.adjustmentThreshold" class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors text-sm" @click="reconcile">
          Reconcile with Adjustment
        </q-btn>
        <q-btn class="px-3 py-1.5 bg-red-500 text-white text-sm rounded-md hover:bg-red-600 transition-colors" @click="closeTDSAndRemarks">
          Cancel
        </q-btn>
      </div>
    </q-card>
  </q-dialog>
</template>
