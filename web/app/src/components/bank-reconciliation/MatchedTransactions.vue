<script setup lang="ts">
import { Ref } from 'vue'
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

const props = defineProps({
  startDate: {
    type: String,
    required: true
  },
  endDate: {
    type: String,
    required: true
  },
  accountId: {
    type: Number,
    required: true
  },
  filterSources: {
    type: Function,
    required: true
  },
  calculateTotal: {
    type: Function,
    required: true
  },
  calculateTotalFromCounterparts: {
    type: Function,
    required: true
  }
})


interface StatementTransactionData {
  id: number
  date: string
  dr_amount: string | null
  cr_amount: string | null
  balance: string
  description: string
  transaction_ids: number[]
}

interface GroupedTransaction {
  statement_transactions: StatementTransactionData[]
  system_transactions: SystemTransactionData[]
}

type Response = {
  results: GroupedTransaction[]
  pagination: {
    page: number
    pages: number
  }
}
// const matchedTransactions: Ref<GroupedTransaction[]> = ref([])
const data: Ref<Response> = ref({
  results: [],
  pagination: {
    page: 1,
    pages: 1
  }
})
const page = ref(1)

const fetchData = () => {
  const endpoint = `/v1/bank-reconciliation/matched-transactions/?start_date=${props.startDate}&end_date=${props.endDate}&account_id=${props.accountId}&page=${page.value}`
  useApi(endpoint).then((response) => {
    data.value = response
    page.value = response.pagination.page
  }).catch((error) => {
    console.log(error)
    data.value.results = []
  })
}

fetchData()



const reconcileMatchedTransactions = (matchedTransaction: {
  statement_transactions: StatementTransactionData[]
  system_transactions: SystemTransactionData[]
}) => {
  console.log('Reconciling:', matchedTransaction)
  useApi('v1/bank-reconciliation/reconcile-transactions/', {
    method: 'POST',
    body: {
      statement_ids: matchedTransaction.statement_transactions.map(t => t.id),
      transaction_ids: matchedTransaction.system_transactions.map(t => t.id),
    }
  }).then(() => {
    const index = data.value?.results.findIndex(group => group === matchedTransaction)
    if (index > -1) {
      data.value?.results.splice(index, 1)
    }
    $q.notify({
      color: 'green-6',
      message: 'Transactions reconciled successfully',
      icon: 'check_circle',
      position: 'top-right',
    })
  }).catch((error) => {
    console.log(error)
    $q.notify({
      color: 'red-6',
      message: 'Failed to reconcile transactions',
      icon: 'error',
      position: 'top-right',
    })
  })
}


const unmatchMatchedTransactions = (matchedTransaction: {
  statement_transactions: StatementTransactionData[]
  system_transactions: SystemTransactionData[]
}) => {
  console.log('Unmatching:', matchedTransaction)
  useApi('v1/bank-reconciliation/unmatch-transactions/', {
    method: 'POST',
    body: {
      statement_ids: matchedTransaction.statement_transactions.map(t => t.id),
    }
  }).then(() => {
    // matchedTransaction.statementTransactions.forEach(t => {
    //   unmatchedStatementTransactions.value.push(t)
    // })
    // matchedTransaction.systemTransactions.forEach(t => {
    //   unmatchedSystemTransactions.value.push(t)
    // })
    // // remove from groupedTransactions
    const index = data.value?.results.findIndex(group => group === matchedTransaction)
    if (index > -1) {
      data.value?.results.splice(index, 1)
    }
    $q.notify({
      color: 'green-6',
      message: 'Transactions unmatched successfully',
      icon: 'check_circle',
      position: 'top-right',
    })
  }).catch((error) => {
    console.log(error)
    $q.notify({
      color: 'red-6',
      message: 'Failed to unmatch transactions',
      icon: 'error',
      position: 'top-right',
    })
  })
}


</script>

<template>
  <div class="container mx-auto">
    <div class="bg-white shadow-lg rounded-lg overflow-hidden border">
      <div class="p-4 bg-gray-50 max-h-[800px] overflow-y-auto">
        <div v-for="data in data?.results" :key="data.statement_transactions[0].id" class="border-b-2 mb-5 pb-5">
          <div class="grid grid-cols-2 gap-4">
            <!-- Statement Transactions -->
            <div class="flex flex-col">
              <div class="bg-white border rounded-lg shadow-sm overflow-hidden grow">
                <div class="px-4 py-2 border-b bg-blue-50 text-blue-700 font-semibold">
                  Statement
                </div>
                <div class="divide-y text-xs">
                  <div v-for="transaction in data.statement_transactions" :key="transaction.id" class="px-4 py-2.5">
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
                <!-- <span :class="Number(calculateTotal(data.statement_transactions, true)) < 0 ? 'text-red-500' : 'text-green-500'">{{ calculateTotal(data.statement_transactions, true) }}</span> -->
              </div>
            </div>

            <!-- System Transactions -->
            <div class="flex flex-col">
              <div class="bg-white border rounded-lg shadow-sm overflow-hidden grow">
                <div class="px-4 py-2 border-b bg-green-50 text-green-700 font-semibold">
                  System
                  <!-- Add links -->
                  <span v-for="source, index in filterSources(data.system_transactions)" :key="source.source_id">
                    <router-link target="_blank" :to="source.url" class="text-blue-800 decoration-none text-xs">
                      {{ source.source_type }}
                    </router-link>
                    <span v-if="index < filterSources(data.system_transactions).length - 1">, </span>
                  </span>

                </div>
                <div class="divide-y text-sm">
                  <div v-for="transaction, index in data.system_transactions" :key="transaction.id" class="px-4 py-3  border-gray-200 hover:bg-gray-50 transition-colors duration-200 relative group"
                    :class="{ 'border-b': index !== data.system_transactions.length - 1 }">

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
                <span :class="Number(calculateTotalFromCounterparts(data.system_transactions)) < 0 ? 'text-red-500' : 'text-green-500'">{{ calculateTotalFromCounterparts(data.system_transactions)
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
        <div class="q-pa-lg flex justify-end">
          <q-pagination v-model="page" :max="data.pagination.pages" input @update:model-value="fetchData" />
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
