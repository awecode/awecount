<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end" v-if="checkPermissions('PaymentReceiptCreate')">
      <q-btn color="green" to="/payment-receipt/add/" label="New Receipt" icon-right="add" />
    </div>
    <q-table title="Income Items" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery"
      v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <!-- <template v-slot:top>
        <div class="search-bar">
          <q-input
            dense
            debounce="500"
            v-model="searchQuery"
            placeholder="Search"
            class="search-bar-wrapper"
          >
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="filterbtn">filters</q-btn>
        </div>
      </template> -->
      <template v-slot:top>
        <div class="search-bar">
          <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="search-bar-wrapper">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="filterbtn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(500px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mx-md">
                    <SelectWithFetch v-model="filters.party" endpoint="v1/parties/choices/" label="Party" />
                  </div>
                  <div class="q-mx-md">
                    <SelectWithFetch v-model="filters.sales_agent" endpoint="v1/sales-agent/choices/"
                      label="Sales Agent" />
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip :options="['Issued', 'Cleared', 'Cancelled']" v-model="filters.status" />
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip label="Mode(s):" :options="['Cheque', 'Cash', 'Bank Deposit']"
                      v-model="filters.mode" />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:startDate="filters.start_date" v-model:endDate="filters.end_date" />
                </div>
                <div class="q-mx-md row q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="q-mr-md" @click="onFilterUpdate"></q-btn>
                  <q-btn color="red" icon="close" @click="resetFilters"></q-btn>
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
              : props.row.status == 'Cleared'
                ? 'bg-green-2 text-green-10'
                : props.row.status == 'Draft'
                  ? 'bg-orange-2 text-orange-10'
                  : props.row.status == 'Cancelled' ? 'bg-red-2 text-red-10' : 'bg-blue-2 text-blue-10'
              " style="border-radius: 8px; padding: 2px 10px">
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-party_name="props">
        <q-td :props="props">
          <div v-if="props.row.customer_name" class="row align-center text-subtitle2 text-grey-8">
            {{ props.row.customer_name }}
          </div>
          <div v-else>
            <q-icon name="domain" size="sm" class="text-grey-8"></q-icon>
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{
              props.row.party_name
            }}</span>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-invoices="props">
        <q-td :props="props">
          <div class="row align-center text-subtitle2 text-grey-8">
            <span v-for=" invoice  in  props.row.invoices " :key="invoice.id">
              <router-link v-if="checkPermissions('SalesView')" class="text-blue" style="text-decoration: none"
                :to="`/sales-voucher/${invoice.id}/view`">
                #{{ invoice.id }}
              </router-link>
              <span v-else>#{{ invoice.id }}</span>
            </span>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-tds_amount="props">
        <q-td :props="props">
          <span>{{ Math.round(props.row.tds_amount * 100) / 100 }}</span>
        </q-td>
      </template>
      <template v-slot:body-cell-amount="props">
        <q-td :props="props">
          <span>{{ Math.round(props.row.amount * 100) / 100 }}</span>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md">
            <q-btn v-if="checkPermissions('PaymentReceiptView')" color="blue" label="View"
              class="q-py-none q-px-md font-size-sm" style="font-size: 12px"
              :to="`/payment-receipt/${props.row.id}/view`" />
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
import usedownloadFile from 'src/composables/usedownloadFile'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  setup() {
    const endpoint = '/v1/payment-receipt/'
    const listData = useList(endpoint)
    const metaData = {
      title: 'Payment Receipts | Awecount',
    }
    useMeta(metaData)
    const onDownloadXls = () => {
      useApi('v1/sales-voucher/export/')
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Credit_Notes'
          )
        )
        .catch((err) => console.log('Error Due To', err))
    }
    const newColumn = [
      { name: 'date', label: 'Date', align: 'left', field: 'date' },
      {
        name: 'party_name',
        label: 'Party',
        align: 'left',
        field: 'party_name',
      },
      { name: 'status', label: 'Status', align: 'center', field: 'status' },
      {
        name: 'mode',
        label: 'Mode',
        align: 'left',
        field: 'mode',
      },
      {
        name: 'amount',
        label: 'Amount',
        align: 'left',
        field: 'amount',
      },
      {
        name: 'tds_amount',
        label: 'TDS',
        align: 'left',
        field: 'tds_amount',
      },
      {
        name: 'invoices',
        label: 'Invoice(s)',
        align: 'left',
        field: 'invoices',
      },
      { name: 'actions', label: 'Actions', align: 'left' },
    ]

    return { ...listData, newColumn, onDownloadXls, checkPermissions }
  },
}
// const {
//   columns,
//   rows,
//   resetFilters,
//   filters,
//   loading,
//   searchQuery,
//   pagination,
//   onRequest,
//   confirmDeletion,
//   initiallyLoaded,
// } = useList(endpoint);
</script>

<style>
.search-bar {
  display: flex;
  width: 100%;
  column-gap: 20px;
}

.search-bar-wrapper {
  width: 100%;
}

.filterbtn {
  width: 100px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
