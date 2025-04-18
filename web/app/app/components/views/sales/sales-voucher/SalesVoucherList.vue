<script lang="ts">
import Decimal from 'decimal.js'

export default {
  setup() {
    const metaData = {
      title: 'Sales Invoices | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/sales-voucher/`
    const listData = useList(endpoint)
    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi(`/api/company/${route.params.company}/sales-voucher/export${query}`)
        .then(data => usedownloadFile(data, 'application/vnd.ms-excel', 'Sales_voucher'))
        .catch(err => console.log('Error Due To', err))
    }
    const newColumn = [
      {
        name: 'voucher_no',
        label: 'Voucher no',
        align: 'left',
        field: 'voucher_no',
        sortable: true,
      },
      {
        name: 'party_name',
        label: 'Party name',
        align: 'left',
        field: 'party_name',
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
        sortable: true,
      },
      { name: 'status', label: 'Status', align: 'center', field: 'status', sortable: true },
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
      {
        name: 'payment_receipts',
        label: 'Receipt(s)',
        align: 'left',
      },
      {
        name: 'receipt_amount',
        label: 'Receipt Amount',
        align: 'left',
      },
      {
        name: 'tds',
        label: 'TDS',
        align: 'left',
      },
      { name: 'actions', align: 'left', label: 'Actions' },
    ]

    const showImportModal = ref(false)
    const importFileRequiredColumns = ['Invoice Group ID', 'Party', 'Customer Name', 'Address', 'Due Date', 'Discount Type', 'Discount', 'Trade Discount', 'Payment Mode', 'Remarks', 'Is Export', 'Sales Agent ID', 'Status', 'Row Item ID', 'Row Quantity', 'Row Rate', 'Row Unit ID', 'Row Discount Type', 'Row Discount', 'Row Tax Scheme ID', 'Row Description']

    return {
      ...listData,
      newColumn,
      Decimal,
      onDownloadXls,
      checkPermissions,
      showImportModal,
      importFileRequiredColumns,
    }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        class="export-btn"
        color="blue"
        icon-right="download"
        label="Export"
        @click="onDownloadXls"
      />
      <q-btn
        class="import-btn"
        color="blue"
        icon-right="upload"
        label="Import"
        @click="showImportModal = true"
      />
      <q-btn
        v-if="checkPermissions('sales.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New Sales"
        :to="`/${$route.params.company}/sales/vouchers/create`"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      :columns="newColumn"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <div class="search-bar">
          <q-input
            v-model="searchQuery"
            dense
            class="full-width search-input"
            debounce="500"
            placeholder="Search"
          >
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
                    <MultiSelectChip v-model="filters.status" :options="['Draft', 'Issued', 'Paid', 'Partially Paid', 'Cancelled']" />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:end-date="filters.end_date" v-model:start-date="filters.start_date" />
                </div>
                <div class="q-mx-sm">
                  <n-auto-complete-v2
                    v-model="filters.payment_mode"
                    label="Payment Mode"
                    :endpoint="`/api/company/${$route.params.company}/payment-modes/choices/`"
                    :fetch-on-mount="true"
                  />
                </div>
                <div class="q-mx-md row q-mb-md q-mt-lg">
                  <q-btn
                    class="q-mr-md f-submit-btn"
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
      <template #body-cell-date="props">
        <q-td data-testid="SN">
          {{ props.row.date }}
        </q-td>
      </template>
      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center" data-testid="status">
            <div
              class="text-white text-subtitle row items-center justify-center"
              style="border-radius: 8px; padding: 2px 10px"
              :class="
                props.row.status === 'Issued' ? 'bg-blue-2 text-blue-10'
                : props.row.status === 'Paid' ? 'bg-green-2 text-green-10'
                  : props.row.status === 'Draft' ? 'bg-orange-2 text-orange-10'
                    : props.row.status === 'Partially Paid' ? 'bg-green-1 text-green-6'
                      : 'bg-red-2 text-red-10'
              "
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>

      <template #body-cell-party_name="props">
        <q-td :props="props">
          <div v-if="props.row.customer_name" class="row align-center text-subtitle2 text-grey-8">
            <!-- We neeed to know show party icons if both customer name and party name is available, as that means customer name is actually an alias of that party -->
            <q-icon
              v-if="props.row.party_name"
              class="text-grey-8 q-mr-sm"
              name="domain"
              size="sm"
            />
            {{ props.row.customer_name }}
          </div>
          <div v-else>
            <q-icon class="text-grey-8" name="domain" size="sm" />
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">
              {{ props.row.party_name }}
            </span>
          </div>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <div class="row q-gutter-x-md justify-start">
            <q-btn
              v-if="checkPermissions('sales.read')"
              class="q-py-none q-px-md font-size-sm l-view-btn"
              color="blue"
              data-testid="view-btn"
              label="View"
              style="font-size: 12px"
              :to="`/${$route.params.company}/sales/vouchers/${props.row.id}`"
            />
          </div>
        </q-td>
      </template>
      <template #body-cell-payment_receipts="props">
        <q-td :props="props">
          <span v-for="id in props.row.payment_receipts.map((item) => item.id)" :key="id">
            <router-link
              v-if="checkPermissions('paymentreceipt.read')"
              class="text-blue"
              style="font-weight: 500; text-decoration: none"
              :to="`/${$route.params.company}/payment-receipts/${id}`"
            >
              #{{ id }}
            </router-link>
            <span v-else>#{{ id }}</span>
          </span>
        </q-td>
      </template>
      <template #body-cell-voucher_no="props">
        <q-td style="padding: 0" :props="props">
          <span v-if="checkPermissions('sales.read')" data-testid="voucher-no">
            <router-link
              v-if="checkPermissions('sales.read') && props.row.voucher_no"
              class="text-blue"
              style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
              :to="`/${$route.params.company}/sales/vouchers/${props.row.id}`"
            >
              {{ props.row.voucher_no }}
            </router-link>
          </span>
          <span v-else data-testid="voucher-no" style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
            {{ props.row.voucher_no }}
          </span>
        </q-td>
      </template>
      <template #body-cell-total_amount="props">
        <q-td>
          <FormattedNumber type="currency" :value="props.row.total_amount" />
        </q-td>
      </template>
      <template #body-cell-receipt_amount="props">
        <q-td>
          <FormattedNumber
            type="currency"
            :value="props.row.payment_receipts.reduce((acc, curr) => acc.add(curr.amount ?? '0'), new Decimal('0')).toNumber()"
          />
        </q-td>
      </template>
      <template #body-cell-tds="props">
        <q-td>
          <FormattedNumber
            type="currency"
            :value="props.row.payment_receipts.reduce((acc, curr) => acc.add(curr.tds_amount ?? '0'), new Decimal('0')).toNumber()"
          />
        </q-td>
      </template>
    </q-table>

    <XLSImport
      v-model:show-import-modal="showImportModal"
      help-text="Upload a .xlsx file to import sales invoices"
      sample-file-url="/files/sales-invoices.xlsx"
      title="Import Sales Vouchers"
      :endpoint="`/api/company/${$route.params.company}/sales-voucher/import/`"
      :required-columns="importFileRequiredColumns"
    />
  </div>
</template>
