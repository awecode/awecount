<template>
  <div class="q-pa-md">
    <q-table
      title="Income Items"
      :rows="rows"
      :columns="newColumn"
      :loading="loading"
      :filter="searchQuery"
      v-model:pagination="pagination"
      row-key="id"
      @request="onRequest"
      class="q-mt-md"
      rows-per-page-options
    >
      <template v-slot:top>
        <div
          class="row q-col-gutter-md full-width"
          style="justify-content: space-between"
        >
          <div class="row q-col-gutter-md">
            <q-input label="From Date"> </q-input>
            <q-input label="To Date"> </q-input>
            <div class="row items-end">
              <q-btn label="Filter" color="green"></q-btn>
            </div>
          </div>
          <div class="row items-end" v-if="aggregate">
            <q-btn
              label="Export Xls"
              color="blue"
              icon-right="download"
              @click="onDownloadXls"
            ></q-btn>
          </div>
        </div>
      </template>

      <template v-slot:body-cell-voucher_no="props">
        <q-td :props="props">
          <div class="row align-center">
            <router-link
              style="font-weight: 500; text-decoration: none"
              class="text-blue"
              :to="`/sales-voucher/${props.row.voucher_no}/view`"
            >
              {{ props.row.voucher_no }}
            </router-link>
          </div>
        </q-td>
      </template>
      <template v-slot:header="props">
        <q-tr>
          <q-th colspan="4" style="text-align: center">Invoice</q-th>
          <q-th rowspan="2" style="text-align: center">Total Sales</q-th>
          <q-th
            rowspan="2"
            style="text-align: center"
            :style="{ 'white-space': 'normal' }"
            >Non Taxable Sales</q-th
          >
          <q-th
            rowspan="2"
            style="text-align: center"
            :style="{ 'white-space': 'normal' }"
            >Export Sales</q-th
          >
          <q-th rowspan="2" style="text-align: center">Discount</q-th>
          <q-th rowspan="1" colspan="2" style="text-align: center"
            >Taxable Sales</q-th
          >
        </q-tr>
        <q-tr>
          <q-th
            v-for="header in props.cols"
            :key="header.name"
            :style="
              header.remove === true
                ? {
                    display: 'none',
                  }
                : ''
            "
            ><span>{{ header.label }}</span></q-th
          >
          <!-- <q-th :props="props" key="SalesCount">Biil No.</q-th>
          <q-th :props="props" key="DailySales">Buyers's Name</q-th>
          <q-th :props="props" key="BeforeOrderQty">Stock</q-th>
          <q-th :props="props" key="BeforeOrderDays">Days</q-th>
          <q-th :props="props" key="BeforeOrderDate">Date</q-th>
          <q-th :props="props" key="AfterOrderQty">Stock</q-th>
          <q-th :props="props" key="AfterOrderDays">Days</q-th>
          <q-th :props="props" key="AfterOrderDate">Date</q-th>
          <q-th :props="props" key="Price">Price</q-th>
          <q-th :props="props" key="Discount">Discount</q-th>
          <q-th :props="props" key="Total">Total</q-th> -->
        </q-tr>
      </template>
    </q-table>
    <!-- {{ aggregate }} -->
    <q-card class="q-mt-md" v-if="aggregate">
      <q-card-section>
        <div>
          <h5 class="q-ma-none q-ml-sm text-weight-bold text-grey-9">
            Aggregate Report for Filtered Data
          </h5>
        </div>
        <hr />
        <div class="q-mt-md">
          <div class="row q-mb-md" v-for="(value, key) in aggregate" :key="key">
            <div class="col-6">
              <div class="text-weight-medium text-grey-9 text-capitalize">
                {{
                  key.replace('__', ' ').replace('__', ' ').replace('_', ' ')
                }}
              </div>
            </div>
            <div class="col-6">
              <div class="text-weight-bold">{{ value }}</div>
            </div>
          </div>
          <!-- <div class="row">
            <div class="col-6">
              <span class="text-weight-medium text-grey-9"
                >Total Sales Invoice(s) Issued</span
              >
            </div>
            <div class="col-6">
              <span class="text-weight-bold"> 15 </span>
            </div>
          </div> -->
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script lang="ts">
import useList from '/src/composables/useList'
export default {
  setup() {
    const route = useRoute()
    const endpoint = '/v1/sales-book/'
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
        name: 'buyers_name',
        label: 'Buyer',
        align: 'left',
        field: 'buyers_name',
      },
      {
        name: 'buyers_pan',
        label: 'Tax No.',
        align: 'left',
        field: 'buyers_pan',
      },
      {
        name: 'total_sales',
        remove: true,
        label: 'Total Sales',
        align: 'left',
        field: (row) => row.voucher_meta.grand_total,
      },
      {
        name: 'non_taxable_sales',
        remove: true,
        label: 'Non Taxable Sales',
        align: 'left',
        field: (row) => row.voucher_meta.non_taxable,
      },
      {
        name: 'export_sales',
        remove: true,
        label: 'Non Taxable Sales',
        align: 'left',
        field: '',
      },
      // TODO: add export sales
      {
        name: 'discount',
        label: 'Discount',
        align: 'left',
        field: 'meta_discount',
        remove: true,
      },
      {
        name: 'amount',
        label: 'Amount',
        align: 'left',
        field: 'meta_taxable',
      },
      {
        name: 'tax',
        label: 'Tax',
        align: 'left',
        field: 'meta_tax',
      },
    ]
    const onDownloadXls = () => {
      const downloadEndpoint = route.fullPath.slice(route.fullPath.indexOf('?'))
      debugger
      useApi('v1/sales-book/export/' + downloadEndpoint)
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Sales Book'
          )
        )
        .catch((err) => console.log('Error Due To', err))
    }
    return {
      ...listData,
      newColumn,
      onDownloadXls,
    }
  },
}
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
