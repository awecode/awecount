<script setup lang="ts">
import { Ref } from 'vue'
const route = useRoute()

interface StatementInfo {
  account: {
    name: string
  },
  date: {
    start: string,
    end: string
  },
  total_reconciled: number,
  total_unreconciled: number
}


const statementInfo: Ref<StatementInfo | null> = ref(null)

useApi(`v1/bank-reconciliation/${route.params.id}/statement-info/`).then((response) => {
  statementInfo.value = response
})

const endpoint = `v1/bank-reconciliation/${route.params.id}/`
const {
  rows,
  filters,
  loading,
  searchQuery,
  pagination,
  onFilterUpdate,
  resetFilters,
  onRequest,
} = useList(endpoint)

type align = 'left' | 'center' | 'right'
const columns = [
  {
    name: 'date',
    align: 'center' as align,
    label: 'Date',
    field: 'date',
    sortable: true
  },
  {
    name: 'description',
    align: 'left' as align,
    label: 'Description',
    field: 'description',
    sortable: true
  },
  {
    name: 'Debit',
    align: 'left' as align,
    label: 'Debit',
    field: 'dr_amount',
    sortable: true
  },
  {
    name: 'Credit',
    align: 'left' as align,
    label: 'Credit',
    field: 'cr_amount',
    sortable: true
  },
  {
    name: 'status',
    align: 'center' as align,
    label: 'Status',
    field: 'status',
    sortable: true
  },
]



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
            <!-- Date Range -->
            <div class="flex items-center justify-center md:justify-start text-gray-500 mt-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span class="text-sm">{{ statementInfo?.date.start }} - {{ statementInfo?.date.end }}</span>
            </div>
          </div>

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
        </div>
      </div>
    </div>


    <div class="q-pa-md">
      <q-table :rows="rows" :columns="columns" :loading="loading" :filter="searchQuery" v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
        <template v-slot:top>
          <div class="search-bar">
            <q-input dense debounce="500" v-model="searchQuery as string" placeholder="Search" class="full-width search-input">
              <template v-slot:append>
                <q-icon name="search" />
              </template>
            </q-input>
            <q-btn class="f-open-btn" icon="mdi-filter-variant">
              <q-menu>
                <div class="menu-wrapper" style="width: min(500px, 90vw)">
                  <div style="border-bottom: 1px solid lightgrey">
                    <h6 class="q-ma-md text-grey-9">Filters</h6>
                  </div>
                  <div class="q-ma-sm">
                    <div class="q-ma-sm">
                      <MultiSelectChip :options="['Reconciled', 'Matched', 'Unreconciled']" v-model="filters.status" />
                    </div>
                    <div class="q-mx-md">
                      <DateRangePicker v-model:startDate="filters.start_date" v-model:endDate="filters.end_date" />
                    </div>
                  </div>
                  <div class="q-mx-md flex gap-4 q-mb-md">
                    <q-btn color="green" label="Filter" @click="onFilterUpdate" class="f-submit-btn"></q-btn>
                    <q-btn color="red" icon="close" @click="resetFilters" class="f-reset-btn"></q-btn>
                  </div>
                </div>
              </q-menu>
            </q-btn>
          </div>
        </template>
        <!--  -->
        <template v-slot:body-cell-status="props">
          <td class="text-center">
            <q-chip :color="props.row.status === 'Reconciled' ? 'green' : props.row.status === 'Matched' ? 'orange' : 'red'" class="text-white" :label="props.row.status" />
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
