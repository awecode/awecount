<script setup lang="ts">
const route = useRoute()
const accountDateInfo = ref(null)

useApi(`v1/bank-reconciliation/${route.params.id}/account-and-dates-info/`).then((response) => {
  accountDateInfo.value = response
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
    <div class="bg-blue-50 px-6 py-2 border-b border-blue-100">
      <div class="flex items-center">
        <h2 class="text-lg font-bold text-blue-800">
          <span>
            {{ accountDateInfo?.account?.name }} </span>
        </h2>
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
