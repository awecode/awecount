<script>
export default {
  setup() {
    const metaData = {
      title: 'Purchases/Expenses | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/purchase-vouchers/`
    const listData = useList(endpoint)
    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi(`/api/company/${route.params.company}/purchase-vouchers/export${query}`)
        .then(data =>
          usedownloadFile(
            data,
            'application/vnd.ms-excel',
            'Purchase_voucher',
          ),
        )
        .catch(err => console.log('Error Due To', err))
    }
    const newColumn = [
      {
        name: 'voucher_no',
        label: 'Bill No.',
        align: 'left',
        field: 'voucher_no',
        sortable: true,
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
        sortable: false,
      },
      {
        name: 'total_amount',
        label: 'Total amount',
        align: 'left',
        field: 'total_amount',
        sortable: true,
      },
      { name: 'actions', label: 'Actions', align: 'left' },
    ]

    return { ...listData, onDownloadXls, newColumn, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="flex gap-4 justify-end">
      <q-btn color="blue" label="Export XLS" icon-right="download" class="export-btn" @click="onDownloadXls" />
      <q-btn
        v-if="checkPermissions('purchasevoucher.create')"
        color="green"
        :to="`/${$route.params.company}/purchase-voucher/create/`"
        label="New Purchase"
        icon-right="add"
        class="add-btn"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      title="Income Items"
      :rows="rows"
      :columns="newColumn"
      :loading="loading"
      :filter="searchQuery"
      row-key="id"
      class="q-mt-md"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <div class="search-bar">
          <q-input v-model="searchQuery" dense debounce="500" placeholder="Search" class="full-width search-input">
            <template #append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="f-open-btn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(550px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">
                    Filters
                  </h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mb-sm">
                    <q-checkbox v-model="filters.is_due" label="Is Due?" :false-value="null" />
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip
                      v-model="filters.status"
                      :options="[
                        'Draft',
                        'Issued',
                        'Paid',
                        'Partially Paid',
                        'Cancelled',
                      ]"
                    />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:start-date="filters.start_date" v-model:end-date="filters.end_date" />
                </div>
                <div class="q-mx-sm">
                  <n-auto-complete-v2
                    v-model="filters.payment_mode"
                    :endpoint="`/api/company/${$route.params.company}/payment-modes/choices/`"
                    label="Payment Mode"
                    :fetch-on-mount="true"
                  />
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="f-submit-btn" @click="onFilterUpdate" />
                  <q-btn color="red" icon="close" class="f-reset-btn" @click="resetFilters" />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>

      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center" data-testid="status">
            <div
              class="text-white text-subtitle row items-center justify-center"
              :class="props.row.status == 'Issued'
                ? 'bg-blue-2 text-blue-10'
                : props.row.status == 'Paid'
                  ? 'bg-green-2 text-green-10'
                  : props.row.status == 'Draft'
                    ? 'bg-orange-2 text-orange-10'
                    : 'bg-red-2 text-red-10'
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
          <div>
            <q-icon name="domain" size="sm" class="text-grey-8" />
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{
              props.row.party
            }}</span>
          </div>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div v-if="checkPermissions('purchasevoucher.view')" class="row q-gutter-x-md items-center">
            <q-btn
              color="blue"
              label="View"
              :to="`/${$route.params.company}/purchase-voucher/${props.row.id}/view`"
              class="q-py-none q-px-md font-size-sm l-view-btn"
              style="font-size: 12px"
              data-testid="view-btn"
            />
          </div>
        </q-td>
        <!-- TODO: add modals -->
      </template>
      <template #body-cell-voucher_no="props">
        <q-td :props="props">
          <span v-if="props.row.voucher_no">
            <router-link
              v-if="checkPermissions('purchasevoucher.view')"
              :to="`/${$route.params.company}/purchase-voucher/${props.row.id}/view`"
              style="font-weight: 500; text-decoration: none"
              class="text-blue"
              data-testid="voucher-no"
            >
              {{ props.row.voucher_no }}
            </router-link>
            <span v-else data-testid="voucher-no">{{ props.row.voucher_no }}</span>
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
