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
      :rows-per-page-options="[20]"
    >
      <template v-slot:top>
        <div
          class="row q-col-gutter-md full-width"
          style="justify-content: space-between"
        >
          <div class="row items-center q-gutter-x-md">
            <DateRangePicker
              v-model:startDate="filters.start_date"
              v-model:endDate="filters.end_date"
              :hideBtns="true"
            />
            <div class="row items-center">
              <q-btn
                class="q-mr-md"
                label="Filter"
                color="green"
                @click="onFilterUpdate"
              ></q-btn>
              <q-btn
                v-if="filters.start_date || filters.end_date"
                class="q-mr-md"
                icon="close"
                color="red"
                @click="resetFilters"
              ></q-btn>
            </div>
          </div>
          <div class="row items-center" v-if="aggregate">
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
              :to="`/purchase-voucher/${props.row.id}/view`"
            >
              {{ props.row.voucher_no }}
            </router-link>
          </div>
        </q-td>
      </template>
      <template v-slot:header="props">
        <q-tr>
          <q-th colspan="4" style="text-align: center">Invoice</q-th>
          <q-th rowspan="2" style="text-align: center">Total Purchases</q-th>
          <q-th
            rowspan="2"
            style="text-align: center"
            :style="{ 'white-space': 'normal' }"
            >Non Taxable Purchases</q-th
          >
          <q-th
            rowspan="2"
            style="text-align: center"
            :style="{ 'white-space': 'normal' }"
            >Import Purchases</q-th
          >
          <q-th rowspan="2" style="text-align: center">Discount</q-th>
          <q-th rowspan="1" colspan="2" style="text-align: center"
            >Taxable Purchases</q-th
          >
        </q-tr>
        <q-tr>
          <q-th
            v-for="header in props.cols"
            :key="header.name"
            :style="header.remove === true ? { display: 'none' } : ''"
            ><span>{{ header.label }}</span></q-th
          >
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
                {{ key.replace(/_/g, ' ').replace('meta', '') }}
              </div>
            </div>
            <div class="col-6">
              <div class="text-weight-bold">{{ parseInt((value || 0)) }}</div>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script lang="ts">
import useList from '/src/composables/useList'
export default {
  setup() {
    const metaData = {
      title: 'Purchase Book | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = '/v1/purchase-book/'
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
        label: "Seller's Name",
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
        field: (row) => row.voucher_meta.discount,
        remove: true,
      },
      {
        name: 'amount',
        label: 'Amount',
        align: 'left',
        field: (row) => row.voucher_meta.taxable,
      },
      {
        name: 'tax',
        label: 'Tax',
        align: 'left',
        field: (row) => row.voucher_meta.tax,
      },
    ]
    const onDownloadXls = () => {
      const downloadEndpoint = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi('v1/purchase-book/export/' + downloadEndpoint)
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Purchase_Book'
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

<style scoped lang="scss">
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
