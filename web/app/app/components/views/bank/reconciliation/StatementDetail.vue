<script setup lang="ts">
import type { Ref } from 'vue'
import checkPermissions from '@/composables/checkPermissions'
import { getPermissionFromSourceType, getVoucherUrl } from '@/composables/getVoucherUrlAndPermissions'

const route = useRoute()

interface StatementInfo {
  account: {
    name: string
    id: number
  }
  date: {
    start: string
    end: string
  }
  total_reconciled: number
  total_unreconciled: number
}
const $q = useQuasar()

const statementInfo: Ref<StatementInfo | null> = ref(null)

useApi(`/api/company/${route.params.company}/bank-reconciliation/${route.params.id}/statement-info/`).then((response) => {
  statementInfo.value = response
})

const endpoint = `/api/company/${route.params.company}/bank-reconciliation/${route.params.id}/`
const { rows, filters, loading, searchQuery, pagination, onFilterUpdate, resetFilters, onRequest, loadData } = useList(endpoint)

type align = 'left' | 'center' | 'right'
const columns = [
  {
    name: 'date',
    align: 'center' as align,
    label: 'Dates',
    field: 'date',
    sortable: true,
  },
  {
    name: 'description',
    align: 'left' as align,
    label: 'Description',
    field: 'description',
    sortable: true,
  },
  {
    name: 'Debit',
    align: 'left' as align,
    label: 'Debit',
    field: 'dr_amount',
    sortable: true,
  },
  {
    name: 'Credit',
    align: 'left' as align,
    label: 'Credit',
    field: 'cr_amount',
    sortable: true,
  },
  {
    name: 'SystemTransactions',
    align: 'left' as align,
    label: 'System Transactions',
    field: 'system_transactions',
    sortable: true,
  },
  {
    name: 'status',
    align: 'center' as align,
    label: 'Status',
    field: 'status',
    sortable: true,
  },
  // Action section
  {
    name: 'actions',
    align: 'center' as align,
    label: 'Actions',
    field: 'actions',
  },
]

interface SystemTransactionData {
  id: number
  source_id: number | null
  source_type: string
  description: string
  dr_amount: string | null
  cr_amount: string | null
  status: string
  counterpart_accounts: { dr_amount: string | null, cr_amount: string | null }[]
}

interface StatementTransactionData {
  id: number
  date: string
  description: string
  dr_amount: string | null
  cr_amount: string | null
  status: string
  transaction_ids: number[]
}

const calculateTotalFromCounterparts = (transactions: SystemTransactionData[]) => {
  let cr_amount = 0
  let dr_amount = 0
  for (const transaction of transactions) {
    for (const counterpart of transaction.counterpart_accounts) {
      if (counterpart.cr_amount) {
        cr_amount += Number(counterpart.cr_amount)
      }
      if (counterpart.dr_amount) {
        dr_amount += Number(counterpart.dr_amount)
      }
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
        const url = getVoucherUrl(
          transaction as {
            source_id: number
            source_type: string
          },
        )
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

const unmatchTransactions = async (transactions: StatementTransactionData[]) => {
  $q.dialog({
    title: '<span class="text-blue">Unmatch?</span>',
    message: 'Are you sure you want to unmatch?',
    cancel: true,
    html: true,
  }).onOk(() => {
    useApi(`/api/company/${route.params.company}/bank-reconciliation/unmatch-transactions/`, {
      method: 'POST',
      body: {
        statement_ids: transactions.map(t => t.id),
      },
    })
      .then(() => {
        loadData()
        $q.notify({
          color: 'green-6',
          message: 'Transaction unmatched successfully',
          icon: 'check_circle',
          position: 'top-right',
        })
      })
      .catch((error) => {
        console.log(error)
        $q.notify({
          color: 'red-6',
          message: 'Failed to unmatch the transaction',
          icon: 'error',
          position: 'top-right',
        })
      })
  })
}

const deleteTransactions = async (transactions: StatementTransactionData[]) => {
  $q.dialog({
    title: '<span class="text-red">Delete?</span>',
    message: 'Are you sure you want to delete?',
    cancel: true,
    html: true,
  }).onOk(() => {
    useApi(`/api/company/${route.params.company}/bank-reconciliation/unmatch-transactions/`, {
      method: 'POST',
      body: {
        statement_ids: transactions.map(t => t.id),
      },
    })
      .then(() => {
        loadData()
        $q.notify({
          color: 'green-6',
          message: 'Transaction removed successfully',
          icon: 'check_circle',
          position: 'top-right',
        })
      })
      .catch((error) => {
        console.log(error)
        $q.notify({
          color: 'red-6',
          message: 'Failed to remove the transaction',
          icon: 'error',
          position: 'top-right',
        })
      })
  })
}
</script>

<template>
  <div class="bg-white shadow-lg rounded-xl overflow-hidden p-6">
    <!-- Account Header -->
    <div class="bg-gradient-to-r from-blue-50 to-blue-100 shadow-lg border border-blue-200 rounded-lg">
      <div class="mx-auto px-6 py-5">
        <div class="flex flex-col md:flex-row justify-between items-center space-y-5 md:space-y-0">
          <!-- Account Name Section -->
          <div class="text-center md:text-left">
            <h2 class="text-2xl font-bold text-blue-800 tracking-tight mt-0 mb-2">
              {{ statementInfo?.account?.name || 'Account Statement' }}
            </h2>

            <div class="flex items-center justify-center md:justify-start text-gray-500 mt-2">
              <svg
                class="h-5 w-5 mr-2 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                />
              </svg>
              <span class="text-sm">{{ statementInfo?.date.start }} - {{ statementInfo?.date.end }}</span>
            </div>
          </div>

          <div class="flex flex-col gap-4 items-center">
            <!-- Summary Info -->
            <div class="grid grid-cols-2 md:grid-cols-2 gap-4">
              <!-- Reconciled -->
              <div class="flex flex-col items-center text-center md:items-start md:text-left">
                <span class="text-sm font-medium text-gray-600">Reconciled</span>
                <span class="text-lg font-semibold text-blue-700">
                  {{ statementInfo?.total_reconciled }}
                </span>
              </div>
              <!-- Unreconciled -->
              <div class="flex flex-col items-center text-center md:items-start md:text-left">
                <span class="text-sm font-medium text-gray-600">Unreconciled</span>
                <span class="text-lg font-semibold text-red-600">
                  {{ statementInfo?.total_unreconciled }}
                </span>
              </div>
            </div>
            <div class="w-full">
              <q-btn
                v-if="!!statementInfo?.total_unreconciled"
                class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn w-full"
                color="blue"
                label="Reconcile remaining"
                style="font-size: 12px"
                :to="`/${$route.params.company}/banking/reconciliation/reconcile?account_id=${statementInfo.account.id}&start_date=${statementInfo?.date.start}&end_date=${statementInfo?.date.end}`"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="q-pa-md">
      <q-table
        v-model:pagination="pagination"
        class="q-mt-md"
        row-key="id"
        :columns="columns"
        :filter="searchQuery"
        :loading="loading"
        :rows="rows"
        :rows-per-page-options="[20]"
        @request="onRequest"
      >
        <template #top>
          <div class="search-bar">
            <q-input
              dense
              class="full-width search-input"
              debounce="500"
              placeholder="Search"
              :model-value="searchQuery"
              @update:model-value="($event) => searchQuery = $event"
            >
              <template #append>
                <q-icon name="search" />
              </template>
            </q-input>
            <q-btn class="f-open-btn" icon="mdi-filter-variant">
              <q-menu>
                <div class="menu-wrapper" style="width: min(500px, 90vw)">
                  <div style="border-bottom: 1px solid lightgrey">
                    <h6 class="q-ma-md text-grey-9">
                      Filters
                    </h6>
                  </div>
                  <div class="q-ma-sm">
                    <div class="q-ma-sm">
                      <MultiSelectChip v-model="filters.status" :options="['Reconciled', 'Matched', 'Unreconciled']" />
                    </div>
                    <div class="q-mx-md">
                      <DateRangePicker v-model:end-date="filters.end_date" v-model:start-date="filters.start_date" />
                    </div>
                  </div>
                  <div class="q-mx-md flex gap-4 q-mb-md">
                    <q-btn
                      class="f-submit-btn"
                      color="green"
                      label="Filter"
                      @click="onFilterUpdate"
                    />
                    <q-btn
                      class="f-reset-btn"
                      color="red"
                      icon="close"
                      @click="resetFilters"
                    />
                  </div>
                </div>
              </q-menu>
            </q-btn>
          </div>
        </template>
        <!--  -->
        <template #body-cell-date="props">
          <td class="text-center">
            <div v-for="transaction in props.row.statement_transactions" :key="transaction.id" class="text-xs">
              <div class="text-gray-800">
                {{ transaction.date }}
              </div>
            </div>
          </td>
        </template>
        <template #body-cell-description="props">
          <td>
            <div v-for="transaction in props.row.statement_transactions" :key="transaction.id" class="text-xs">
              <div class="text-gray-800">
                {{ transaction.description }}
              </div>
            </div>
          </td>
        </template>
        <template #body-cell-Debit="props">
          <td>
            <div v-for="transaction in props.row.statement_transactions" :key="transaction.id" class="text-xs">
              <div class="text-red-500 font-medium">
                {{ transaction.dr_amount?.toFixed(2) || '-' }}
              </div>
            </div>
            <!-- Show total -->
            <div v-if="props.row.statement_transactions?.filter(t => t.dr_amount)?.length > 1" class="font-medium text-red-500 w-fit !text-left" style="border-top: 1px solid gray;">
              {{ props.row.statement_transactions.reduce((acc, curr) => acc + Number(curr.dr_amount), 0).toFixed(2) }}
            </div>
          </td>
        </template>
        <template #body-cell-Credit="props">
          <td>
            <div v-for="transaction in props.row.statement_transactions" :key="transaction.id" class="text-xs">
              <div class="text-green-500 font-medium">
                {{ transaction.cr_amount?.toFixed(2) }}
              </div>
            </div>
            <div v-if="props.row.statement_transactions.filter(t => t.cr_amount)?.length > 1" class="font-medium text-red-500 w-fit !text-left" style="border-top: 1px solid gray;">
              {{ props.row.statement_transactions.reduce((acc, curr) => acc + Number(curr.cr_amount), 0).toFixed(2) }}
            </div>
          </td>
        </template>
        <template #body-cell-SystemTransactions="props">
          <td>
            <div>
              <div v-if="props.row.system_transactions.length" class="flex justify-between items-center">
                <div>
                  <div v-for="(source, index) in filterSources(props.row.system_transactions)" :key="source.source_id">
                    <router-link class="text-blue-800 decoration-none text-xs" target="_blank" :to="source.url">
                      {{ source.source_type }}
                    </router-link>
                    <span v-if="index < filterSources(props.row.system_transactions).length - 1">,</span>
                  </div>
                </div>
                <div class="px-4 py-2 font-medium">
                  <div class="space-y-1" style="border-bottom: 1px solid gray">
                    <div v-for="transactionData in props.row.system_transactions" :key="transactionData.id">
                      <div v-for="counterpart in transactionData.counterpart_accounts" :key="counterpart.account_id" class="flex justify-between items-center text-xs">
                        <div class="text-gray-700 truncate pr-2">
                          {{ counterpart.account_name }}
                        </div>

                        <div class="flex space-x-2">
                          <span v-if="counterpart.dr_amount" class="text-red-600 font-medium">-{{ counterpart.dr_amount }}</span>
                          <span v-if="counterpart.cr_amount" class="text-green-600 font-medium">+{{ counterpart.cr_amount }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-if="props.row.system_transactions.length" class="text-right w-full" :class="Number(calculateTotalFromCounterparts(props.row.system_transactions)) < 0 ? 'text-green-500' : 'text-red-500'">
                    {{ calculateTotalFromCounterparts(props.row.system_transactions).replaceAll('-', '') }}
                  </div>
                </div>
              </div>
              <div v-else class="px-4 py-2 font-medium">
                -
              </div>
            </div>
          </td>
        </template>

        <template #body-cell-status="props">
          <td class="text-center">
            <q-chip
              class="text-white"
              :color="
                props.row.statement_transactions[0].status === 'Reconciled' ? 'green'
                : props.row.statement_transactions[0].status === 'Matched' ? 'orange'
                  : 'red'
              "
              :label="props.row.statement_transactions[0].status"
            />
          </td>
        </template>
        <template #body-cell-actions="props">
          <td class="text-end">
            <q-btn
              v-if="props.row.statement_transactions[0].status === 'Matched' || props.row.statement_transactions[0].status === 'Reconciled'"
              color="blue"
              label="Unmatch"
              @click="unmatchTransactions(props.row.statement_transactions)"
            />
            <q-btn
              class="ml-2"
              color="red"
              icon="delete"
              @click="deleteTransactions(props.row.statement_transactions)"
            />
          </td>
        </template>
      </q-table>
    </div>

    <!-- No Transactions State -->
    <div v-if="rows?.length === 0" class="text-center py-10 text-gray-500">
      <p class="text-sm font-medium">
        No transactions found.
      </p>
    </div>
  </div>
</template>
