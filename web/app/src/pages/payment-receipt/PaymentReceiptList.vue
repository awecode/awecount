<script>
import checkPermissions from 'src/composables/checkPermissions'
import usedownloadFile from 'src/composables/usedownloadFile'
import useList from 'src/composables/useList'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/payment-receipt/`
    const listData = useList(endpoint)
    const metaData = {
      title: 'Payment Receipts | Awecount',
    }
    useMeta(metaData)
    const onDownloadXls = () => {
      useApi(`/api/company/${$route.params.company}/sales-voucher/export`)
        .then((data) => usedownloadFile(data, 'application/vnd.ms-excel', 'Credit_Notes'))
        .catch((err) => console.log('Error Due To', err))
    }
    const newColumn = [
      { name: 'date', label: 'Date', align: 'left', field: 'date', sortable: true },
      {
        name: 'party_name',
        label: 'Party',
        align: 'left',
        field: 'party_name',
      },
      { name: 'status', label: 'Status', align: 'center', field: 'status', sortable: true },
      {
        name: 'mode',
        label: 'Mode',
        align: 'left',
        field: 'mode',
        sortable: true,
      },
      {
        name: 'amount',
        label: 'Amount',
        align: 'left',
        field: 'amount',
        sortable: true,
      },
      {
        name: 'tds_amount',
        label: 'TDS',
        align: 'left',
        field: 'tds_amount',
        sortable: true,
      },
      {
        name: 'invoices',
        label: 'Invoice(s)',
        align: 'left',
        field: 'invoices',
        sortable: true,
      },
      { name: 'actions', label: 'Actions', align: 'left' },
    ]

    return { ...listData, newColumn, onDownloadXls, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div v-if="checkPermissions('paymentreceipt.create')" class="row q-gutter-x-md justify-end">
      <q-btn color="green" :to="`/${$route.params.company}/payment-receipt/create/`" label="New Receipt" icon-right="add" class="add-btn" />
    </div>
    <q-table v-model:pagination="pagination" title="Income Items" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" row-key="id" class="q-mt-md" :rows-per-page-options="[20]" @request="onRequest">
      <template #top>
        <div class="search-bar">
          <q-input v-model="searchQuery" dense debounce="500" placeholder="Search" class="full-width search-input">
            <template #append>
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
                  <div class="q-mx-md">
                    <n-auto-complete-v2 v-model="filters.party" :fetch-on-mount="true" :endpoint="`/api/company/${$route.params.company}/parties/choices/`" label="Party" />
                  </div>
                  <div class="q-mx-md">
                    <n-auto-complete-v2 v-model="filters.sales_agent" :fetch-on-mount="true" :endpoint="`/api/company/${$route.params.company}/sales-agent/choices/`" label="Sales Agent" />
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip v-model="filters.status" :options="['Issued', 'Cleared', 'Cancelled']" />
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip v-model="filters.mode" label="Mode(s):" :options="['Cheque', 'Cash', 'Bank Deposit']" />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:start-date="filters.start_date" v-model:end-date="filters.end_date" />
                </div>
                <div class="q-mx-md row q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="q-mr-md f-submit-btn" @click="onFilterUpdate" />
                  <q-btn color="red" icon="close" class="f-reset-btn" @click="resetFilters" />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>

      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center">
            <div
              class="text-white text-subtitle row items-center justify-center"
              :class="
                props.row.status == 'Issued' ? 'bg-blue-2 text-blue-10'
                : props.row.status == 'Cleared' ? 'bg-green-2 text-green-10'
                : props.row.status == 'Draft' ? 'bg-orange-2 text-orange-10'
                : props.row.status == 'Cancelled' ? 'bg-red-2 text-red-10'
                : 'bg-blue-2 text-blue-10'
              "
              style="border-radius: 8px; padding: 2px 10px"
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>

      <template #body-cell-party_name="props">
        <q-td :props="props">
          <div v-if="props.row.customer_name" class="row align-center text-subtitle2 text-grey-8">
            {{ props.row.customer_name }}
          </div>
          <div v-else>
            <q-icon name="domain" size="sm" class="text-grey-8" />
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{ props.row.party_name }}</span>
          </div>
        </q-td>
      </template>
      <template #body-cell-invoices="props">
        <q-td :props="props">
          <div class="row align-center text-subtitle2 text-grey-8">
            <span v-for="invoice in props.row.invoices" :key="invoice.id">
              <router-link v-if="checkPermissions('sales.view')" class="text-blue" style="text-decoration: none" :to="`/${$route.params.company}/sales-voucher/${invoice.id}/view`">#{{ invoice.voucher_no }}</router-link>
              <span v-else>#{{ invoice.voucher_no }}</span>
            </span>
          </div>
        </q-td>
      </template>
      <template #body-cell-tds_amount="props">
        <q-td :props="props">
          <span>{{ $nf(props.row.tds_amount) }}</span>
        </q-td>
      </template>
      <template #body-cell-amount="props">
        <q-td :props="props">
          <span>{{ $nf(props.row.amount) }}</span>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md">
            <q-btn v-if="checkPermissions('paymentreceipt.view')" color="blue" label="View" class="q-py-none q-px-md font-size-sm l-view-btn" style="font-size: 12px" :to="`/${$route.params.company}/payment-receipt/${props.row.id}/view`" />
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
