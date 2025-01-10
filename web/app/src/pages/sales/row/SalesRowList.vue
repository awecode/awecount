<template>
  <div class="q-pa-md">
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
              <div class="menu-wrapper" style="width: min(500px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mx-md">
                    <DateRangePicker v-model:startDate="filters.start_date" v-model:endDate="filters.end_date" />
                  </div>
                  <div class="q-mx-sm">
                    <n-auto-complete-v2 v-model="filters.category" label="Sales Agent"
                      :endpoint="`v1/sales-agent/choices`" fetchOnMount />
                  </div>
                  <div class="q-mx-sm">
                    <n-auto-complete-v2 v-model="filters.party" endpoint="v1/parties/choices" label="Party"
                      fetchOnMount />
                  </div>
                  <div class="q-mx-sm">
                    <n-auto-complete-v2 v-model="filters.tax_scheme" endpoint="v1/tax_scheme/choices/"
                      label="Tax Scheme" fetchOnMount />
                  </div>
                  <div class="q-mx-sm">
                    <n-auto-complete-v2 v-model="filters.item_category" endpoint="v1/inventory-categories/choices/"
                      label="Item Category" fetchOnMount />
                  </div>
                  <div class="q-mx-sm">
                    <SelectWithFetch v-model="filters.item" endpoint="v1/items/sales-choices/" label="Items" />
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
                <div class="q-mx-md flex gap-4 q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="f-submit-btn" @click="onFilterUpdate"></q-btn>
                  <q-btn color="red" icon="close" class="f-reset-btn" @click="resetFilters"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>

      <template v-slot:body-cell-voucher_id="props">
        <q-td :props="props" style="padding: 0;">
          <div class="row align-center" style="height: 100%;">
            <router-link v-if="checkPermissions('SalesView')" :to="`/sales-voucher/${props.row.voucher_id}/view`"
              style="font-weight: 500; text-decoration: none; display: flex; align-items: center; padding: 8px 8px 8px 16px;"
              class="text-blue l-view-btn">
              {{ props.row.voucher__voucher_no }}
            </router-link>
            <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px;">
              {{ props.row.voucher__voucher_no }}
            </span>
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
      <template v-slot:body-cell-voucher__date="props">
        <q-td :props="props">
          {{ store.isCalendarInAD ? props.row.voucher__date : DateConverter.getRepresentation(props.row.voucher__date,
            'bs') }}
        </q-td>
      </template>
    </q-table>
    <q-card class="q-mt-md" v-if="aggregate">
      <q-card-section>
        <div>
          <h5 class="q-ma-none q-ml-sm text-weight-bold text-grey-9">
            Aggregate Report for Filtered Data
          </h5>
        </div>
        <hr />
        <div class="q-mt-md">
          <div class="row q-mb-md" v-for="header in aggregate_headers" :key="header[0]">
            <div class="col-6">
              <div class="text-weight-medium text-grey-9">
                {{ header[0] }}
              </div>
            </div>
            <div class="col-6">
              <div class="text-weight-bold">{{ parseInt((aggregate?.[header[1]] || 0).toFixed(2)) }}</div>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>
    <!-- {{ store.isCalendarInAD }} -->
  </div>
</template>

<script lang="ts">
import useList from '/src/composables/useList'
import MultiSelectChip from '/src/components/filter/MultiSelectChip.vue'
import checkPermissions from 'src/composables/checkPermissions'
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
// import ListFilter from '/src/components/sales/row/ListFilter.vue'
import { Ref } from 'vue'
export default {
  setup() {
    const store = useLoginStore()
    const endpoint = '/v1/sales-row/'
    const listData = useList(endpoint)
    const metaData = {
      title: 'Sales Rows | Awecount',
    }
    useMeta(metaData)
    const newColumn = [
      {
        name: 'voucher_id',
        label: 'Bill No',
        align: 'left',
        field: 'voucher_id',
        sortable: true
      },
      {
        name: 'voucher__date',
        label: 'Date',
        align: 'left',
        field: 'voucher__date',
        sortable: true
      },
      {
        name: 'buyers_name',
        label: 'Buyer',
        align: 'left',
        field: 'buyers_name',
        sortable: true
      },
      {
        name: 'item',
        label: 'Item',
        align: 'left',
        field: 'item',
        sortable: true
      },
      {
        name: 'quantity',
        label: 'Quantity',
        align: 'left',
        field: 'quantity',
        sortable: true
      },
      {
        name: 'rate',
        label: 'Rate',
        align: 'left',
        field: 'rate',
        sortable: true
      },
      {
        name: 'discount_amount',
        label: 'Discount',
        align: 'left',
        field: 'discount_amount',
        sortable: true
      },
      {
        name: 'tax_amount',
        label: 'Tax',
        align: 'left',
        field: 'tax_amount',
        sortable: true
      },
      {
        name: 'net_amount',
        label: 'Amount',
        align: 'left',
        field: 'net_amount',
        sortable: true
      },
    ]
    const fetchedOptions: Ref<Record<string, Array<object> | null>> = ref({
      'sales-agent': null,
      parties: null,
      tax_scheme: null,
      'inventory-categories': null,
      item_choices: null,
    })
    const aggregate_headers = [
      ['Total Sales Invoice(s) Issued', 'voucher__count'],
      ['Taxable Sales Amount', 'sales_after_tax'],
      ['Tax in Sales', 'tax_amount__sum'],
      ['Net Sales Amount', 'net_amount__sum'],
      ['Total Discounted Amount', 'discount_amount__sum'],
      ['Total Quantity Sold', 'quantity__sum'],
      ['Unique Items Sold', 'item__count'],
      ['Customer(s)', 'voucher__party__count'],
      ['Average Selling Price', 'rate__avg'],
      ['Sales Agent(s)', 'voucher__sales_agent__count']
    ]
    return {
      ...listData,
      newColumn,
      fetchedOptions,
      MultiSelectChip,
      checkPermissions,
      store,
      DateConverter,
      aggregate_headers
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
