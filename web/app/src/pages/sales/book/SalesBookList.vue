<script lang="ts">
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/sales-book/`
    const listData = useList(endpoint)
    const metaData = {
      title: 'Sales Book | Awecount',
    }
    useMeta(metaData)
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
        label: 'Tax Identification No.',
        align: 'left',
        field: 'buyers_pan',
      },
      {
        name: 'total_sales',
        remove: true,
        label: 'Total Sales',
        align: 'left',
        field: row => row.voucher_meta.sub_total_after_row_discounts,
      },
      {
        name: 'non_taxable_sales',
        remove: true,
        label: 'Non Taxable Sales',
        align: 'left',
        field: row => row.voucher_meta.non_taxable,
      },
      {
        name: 'export_sales',
        remove: true,
        label: 'Non Taxable Sales',
        align: 'left',
        field: '',
      },
      // TODO: add export sales
      // {
      //   name: 'discount',
      //   label: 'Discount',
      //   align: 'left',
      //   field: 'meta_discount',
      //   remove: true,
      // },
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
      useApi(`/api/company/${route.params.company}/sales-book/export${downloadEndpoint}`)
        .then(data => usedownloadFile(data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Sales Book'))
        .catch(err => console.log('Error Due To', err))
    }
    return {
      ...listData,
      newColumn,
      onDownloadXls,
      checkPermissions,
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

      <template #header="props">
        <q-tr>
          <q-th colspan="4" style="text-align: center">
            Invoice
          </q-th>
          <q-th rowspan="2" style="text-align: center">
            Total Sales
          </q-th>
          <q-th rowspan="2" style="text-align: center" :style="{ 'white-space': 'normal' }">
            Non Taxable Sales
          </q-th>
          <q-th rowspan="2" style="text-align: center" :style="{ 'white-space': 'normal' }">
            Export Sales
          </q-th>
          <!-- <q-th rowspan="2" style="text-align: center">Discount</q-th> -->
          <q-th colspan="2" rowspan="1" style="text-align: center">
            Taxable Sales
          </q-th>
        </q-tr>
        <q-tr>
          <q-th v-for="header in props.cols" :key="header.name" :style="header.remove === true ? { display: 'none' } : ''">
            <span>{{ header.label }}</span>
          </q-th>
        </q-tr>
      </template>

      <template #body-cell-voucher_no="props">
        <q-td style="padding: 0" :props="props">
          <div class="row align-center" style="height: 100%">
            <router-link
              v-if="checkPermissions('sales.read')"
              class="text-blue l-view-btn"
              style="font-weight: 500; text-decoration: none; display: flex; align-items: center; padding: 8px 8px 8px 16px"
              :to="`/${$route.params.company}/sales/vouchers/${props.row.id}`"
            >
              {{ props.row.voucher_no }}
            </router-link>
            <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
              {{ props.row.voucher_no }}
            </span>
          </div>
        </q-td>
      </template>
      <template #body-cell-total_sales="props">
        <q-td>
          <FormattedNumber type="currency" :value="props.row.voucher_meta.sub_total_after_row_discounts" />
        </q-td>
      </template>
      <template #body-cell-non_taxable_sales="props">
        <q-td>
          <FormattedNumber type="currency" :value="props.row.voucher_meta.non_taxable" />
        </q-td>
      </template>
      <template #body-cell-export_sales="props">
        <q-td>
          <FormattedNumber type="currency" :value="props.row.voucher_meta.export_sales" />
        </q-td>
      </template>
      <template #body-cell-amount="props">
        <q-td>
          <FormattedNumber type="currency" :value="props.row.voucher_meta.amount" />
        </q-td>
      </template>
      <template #body-cell-tax="props">
        <q-td>
          <FormattedNumber type="currency" :value="props.row.voucher_meta.tax" />
        </q-td>
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
