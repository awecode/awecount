<script lang="ts">
export default {
  setup() {
    const metaData = {
      title: 'Purchase Book | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/purchase-book/`
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
      },
      {
        name: 'voucher_no',
        label: 'Bill No',
        align: 'left',
        field: 'voucher_no',
      },
      {
        name: 'sellers_name',
        label: 'Seller\'s Name',
        align: 'left',
        field: 'sellers_name',
      },
      {
        name: 'sellers_pan',
        label: 'Tax No.',
        align: 'left',
        field: 'sellers_pan',
      },
      {
        name: 'total_sales',
        remove: true,
        label: 'Total Purchases',
        align: 'left',
        field: row => row.voucher_meta.grand_total,
      },
      {
        name: 'non_taxable_sales',
        remove: true,
        label: 'Non Taxable Sales',
        align: 'left',
        field: row => row.voucher_meta.non_taxable,
      },
      {
        name: 'import_purchases',
        remove: true,
        label: 'Import Purchases',
        align: 'left',
        field: '',
      },
      // TODO: add export sales
      {
        name: 'discount',
        label: 'Discount',
        align: 'left',
        field: row => row.voucher_meta.discount,
        remove: true,
      },
      {
        name: 'amount',
        label: 'Amount',
        align: 'left',
        field: row => row.voucher_meta.taxable,
      },
      {
        name: 'tax',
        label: 'Tax',
        align: 'left',
        field: row => row.voucher_meta.tax,
      },
    ]
    const onDownloadXls = () => {
      const downloadEndpoint = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi(`/api/company/${route.params.company}/purchase-book/export${downloadEndpoint}`)
        .then(data => usedownloadFile(data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Purchase_Book'))
        .catch(err => console.log('Error Due To', err))
    }
    return {
      ...listData,
      newColumn,
      onDownloadXls,
    }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      title="Income Items"
      :columns="newColumn"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <div class="row q-col-gutter-md full-width" style="justify-content: space-between">
          <div class="row items-center q-gutter-x-md">
            <DateRangePicker v-model:end-date="filters.end_date" v-model:start-date="filters.start_date" :hide-btns="true" />
            <div class="flex gap-4 items-center">
              <q-btn
                class="f-submit-btn"
                color="green"
                label="Filter"
                @click="onFilterUpdate"
              />
              <q-btn
                v-if="filters.start_date || filters.end_date"
                class="f-reset-btn"
                color="red"
                icon="close"
                @click="resetFilters"
              />
            </div>
          </div>
          <div v-if="aggregate" class="row items-center">
            <q-btn
              color="blue"
              icon-right="download"
              label="Export Xls"
              @click="onDownloadXls"
            />
          </div>
        </div>
      </template>

      <template #body-cell-voucher_no="props">
        <q-td style="padding: 0" :props="props">
          <router-link class="text-blue l-view-btn" style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px" :to="`/${$route.params.company}/purchase/vouchers/${props.row.id}`">
            {{ props.row.voucher_no }}
          </router-link>
        </q-td>
      </template>
      <template #header="props">
        <q-tr>
          <q-th colspan="4" style="text-align: center">
            Invoice
          </q-th>
          <q-th rowspan="2" style="text-align: center">
            Total Purchases
          </q-th>
          <q-th rowspan="2" style="text-align: center" :style="{ 'white-space': 'normal' }">
            Non Taxable Purchases
          </q-th>
          <q-th rowspan="2" style="text-align: center" :style="{ 'white-space': 'normal' }">
            Import Purchases
          </q-th>
          <q-th rowspan="2" style="text-align: center">
            Discount
          </q-th>
          <q-th colspan="2" rowspan="1" style="text-align: center">
            Taxable Purchases
          </q-th>
        </q-tr>
        <q-tr>
          <q-th v-for="header in props.cols" :key="header.name" :style="header.remove === true ? { display: 'none' } : ''">
            <span>{{ header.label }}</span>
          </q-th>
        </q-tr>
      </template>
    </q-table>
    <!-- {{ aggregate }} -->
    <q-card v-if="aggregate" class="q-mt-md">
      <q-card-section>
        <div>
          <h5 class="q-ma-none q-ml-sm text-weight-bold text-grey-9">
            Aggregate Report for Filtered Data
          </h5>
        </div>
        <hr />
        <div class="q-mt-md">
          <div v-for="(value, key) in aggregate" :key="key" class="row q-mb-md">
            <div class="col-6">
              <div class="text-weight-medium text-grey-9 text-capitalize">
                {{ key.replace(/_/g, ' ').replace('meta', '') }}
              </div>
            </div>
            <div class="col-6">
              <div class="text-weight-bold">
                {{ parseInt(value || 0) }}
              </div>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>
