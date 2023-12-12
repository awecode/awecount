<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn v-if="checkPermissions('ChequeDepositCreate')" color="green" to="/cheque-deposit/add/"
        label="New Cheque Deposit" class="q-ml-lg add-btn" icon-right="add" />
    </div>

    <q-table title="Cheque Deposits" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery"
      v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <div class="search-bar">
          <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="full-width search-input">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="f-open-btn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(550px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mx-sm">
                    <SelectWithFetch v-model="filters.bank_account" endpoint="v1/bank-account/choices/"
                      label="Bank Account" />
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip v-model="filters.status" :options="['Issued', 'Draft', 'Cleared', 'Cancelled']" />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:startDate="filters.start_date" v-model:endDate="filters.end_date" />
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="f-submit-btn" @click="onFilterUpdate"></q-btn>
                  <q-btn color="red" icon="close" @click="resetFilters" class="f-reset-btn"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center">
            <div class="text-white text-subtitle row items-center justify-center" :class="props.row.status == 'Issued'
              ? 'bg-blue-2 text-blue-10'
              : props.row.status == 'Draft'
                ? 'bg-orange-2 text-orange-10' : props.row.status == 'Cleared'
                  ? 'bg-green-2 text-green-10'
                  : 'bg-red-2 text-red-10'
              " style="border-radius: 8px; padding: 2px 10px">
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn label="View" color="blue" class="q-py-none q-px-md font-size-sm l-view-btn" style="font-size: 12px"
            :to="`/cheque-deposit/${props.row.id}/view/`" />
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
export default {
  setup() {
    const metaData = {
      title: 'Cheque Deposits | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/cheque-deposits/'
    const newColumn = [
      {
        name: 'bank_account_name',
        label: 'Bank Account',
        align: 'left',
        field: 'bank_account_name',
      },
      {
        name: 'benefactor_name',
        label: 'Benefactor',
        align: 'left',
        field: 'benefactor_name',
      },
      {
        name: 'status',
        label: 'Status',
        align: 'center',
        field: 'status',
        sortable: true
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
        sortable: true
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    return { ...useList(endpoint), newColumn, checkPermissions }
  },
}
</script>
