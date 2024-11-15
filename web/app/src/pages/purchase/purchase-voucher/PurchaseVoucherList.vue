<template>
  <div class="q-pa-md">
    <div class="flex gap-4 justify-end">
      <q-btn color="blue" label="Export XLS" icon-right="download" @click="onDownloadXls" class="export-btn" />
      <q-btn v-if="checkPermissions('PurchaseVoucherCreate')" color="green" to="/purchase-voucher/add/"
        label="New Purchase" icon-right="add" class="add-btn" />
    </div>
    <q-table title="Income Items" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery"
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
                  <div class="q-mb-sm">
                    <q-checkbox v-model="filters.is_due" label="Is Due?" :false-value="null"></q-checkbox>
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip :options="[
                      'Draft',
                      'Issued',
                      'Paid',
                      'Partially Paid',
                      'Cancelled',
                    ]" v-model="filters.status" />
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
          <div class="row align-center justify-center" data-testid="status">
            <div class="text-white text-subtitle row items-center justify-center" :class="props.row.status == 'Issued'
              ? 'bg-blue-2 text-blue-10'
              : props.row.status == 'Paid'
                ? 'bg-green-2 text-green-10'
                : props.row.status == 'Draft'
                  ? 'bg-orange-2 text-orange-10'
                  : 'bg-red-2 text-red-10'
              " style="border-radius: 8px; padding: 2px 10px">
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-party_name="props">
        <q-td :props="props">
          <div>
            <q-icon name="domain" size="sm" class="text-grey-8"></q-icon>
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{
              props.row.party
            }}</span>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md items-center" v-if="checkPermissions('PurchaseVoucherView')">
            <q-btn color="blue" label="View" :to="`/purchase-voucher/${props.row.id}/view`"
              class="q-py-none q-px-md font-size-sm l-view-btn" style="font-size: 12px" data-testid="view-btn" />
          </div>
        </q-td>
        <!-- TODO: add modals -->
      </template>
      <template v-slot:body-cell-voucher_no="props">
        <q-td :props="props">
          <span v-if="props.row.voucher_no">
            <router-link v-if="checkPermissions('PurchaseVoucherView')" :to="`/purchase-voucher/${props.row.id}/view`"
              style="font-weight: 500; text-decoration: none" class="text-blue" data-testid="voucher-no">
              {{ props.row.voucher_no }}
            </router-link>
            <span v-else data-testid="voucher-no">{{ props.row.voucher_no }}</span>
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
export default {
  setup() {
    const metaData = {
      title: 'Purchases/Expenses | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/purchase-vouchers/'
    const listData = useList(endpoint)
    const route = useRoute()
    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi('v1/purchase-vouchers/export' + query)
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.ms-excel',
            'Purchase_voucher'
          )
        )
        .catch((err) => console.log('Error Due To', err))
    }
    const newColumn = [
      {
        name: 'voucher_no',
        label: 'Bill No.',
        align: 'left',
        field: 'voucher_no',
        sortable: true
      },
      {
        name: 'party_name',
        label: 'Party',
        align: 'left',
        field: 'party_name',
      },
      { name: 'status', label: 'Status', align: 'center', field: 'status', sortable: true },
      { name: 'date', label: 'Date', align: 'left', field: 'date', sortable: true },
      {
        name: 'payment_mode',
        label: 'Payment Mode',
        align: 'left',
        field: 'payment_mode',
        sortable: false
      },
      {
        name: 'total_amount',
        label: 'Total amount',
        align: 'left',
        field: 'total_amount',
        sortable: true
      },
      { name: 'actions', label: 'Actions', align: 'left' },
    ]

    return { ...listData, onDownloadXls, newColumn, checkPermissions }
  },
}
</script>
