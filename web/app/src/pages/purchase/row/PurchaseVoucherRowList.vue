<script lang="ts">
import type { Ref } from 'vue'
import DateConverter from 'src/components/date/VikramSamvat.js'
import MultiSelectChip from 'src/components/filter/MultiSelectChip.vue'
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'
import { useLoginStore } from 'src/stores/login-info'

export default {
  setup() {
    const store = useLoginStore()
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/purchase-voucher-row/`
    const listData = useList(endpoint)
    const metaData = {
      title: 'PurchaseVoucher Rows | Awecount',
    }
    useMeta(metaData)
    const newColumn = [
      {
        name: 'voucher_id',
        label: 'Bill No',
        align: 'left',
        field: 'voucher_id',
        sortable: true,
      },
      {
        name: 'voucher__date',
        label: 'Date',
        align: 'left',
        field: 'voucher__date',
        sortable: true,
      },
      {
        name: 'buyers_name',
        label: 'Seller',
        align: 'left',
        field: 'buyers_name',
        sortable: true,
      },
      {
        name: 'item',
        label: 'Item',
        align: 'left',
        field: 'item',
        sortable: true,
      },
      {
        name: 'quantity',
        label: 'Quantity',
        align: 'left',
        field: 'quantity',
        sortable: true,
      },
      {
        name: 'rate',
        label: 'Rate',
        align: 'left',
        field: 'rate',
        sortable: true,
      },
      {
        name: 'discount_amount',
        label: 'Discount',
        align: 'left',
        field: 'discount_amount',
        sortable: true,
      },
      {
        name: 'tax_amount',
        label: 'Tax',
        align: 'left',
        field: 'tax_amount',
        sortable: true,
      },
      {
        name: 'net_amount',
        label: 'Amount',
        align: 'left',
        field: 'net_amount',
        sortable: true,
      },
    ]
    const fetchedOptions: Ref<Record<string, Array<object> | null>> = ref({
      'purchase-agent': null,
      'parties': null,
      'tax_scheme': null,
      'inventory-categories': null,
      'item_choices': null,
    })
    const aggregate_headers = [
      ['Total Purchase Invoice(s) Issued', 'voucher__count'],
      ['Taxable Purchase Amount', 'purchase_after_tax'],
      ['Tax in Purchase', 'tax_amount__sum'],
      ['Net Purchase Amount', 'net_amount__sum'],
      ['Total Discounted Amount', 'discount_amount__sum'],
      ['Total Quantity Sold', 'quantity__sum'],
      ['Unique Items Sold', 'item__count'],
      ['Customer(s)', 'voucher__party__count'],
      ['Average Selling Price', 'rate__avg'],
      ['Purchase Agent(s)', 'voucher__purchase_agent__count'],
    ]
    return {
      ...listData,
      newColumn,
      fetchedOptions,
      MultiSelectChip,
      checkPermissions,
      store,
      DateConverter,
      aggregate_headers,
    }
  },
}
</script>

<template>
  <div class="q-pa-md">
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
          <q-input
            v-model="searchQuery"
            dense
            debounce="500"
            placeholder="Search"
            class="full-width search-input"
          >
            <template #append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="f-open-btn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(500px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">
                    Filters
                  </h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mx-md">
                    <DateRangePicker
                      v-model:start-date="filters.start_date"
                      v-model:end-date="filters.end_date"
                    />
                  </div>
                  <div class="q-mx-sm">
                    <NAutoCompleteV2
                      v-model="filters.party"
                      :endpoint="`/api/company/${$route.params.company}/parties/choices`"
                      label="Party"
                      fetch-on-mount
                    />
                  </div>
                  <div class="q-mx-sm">
                    <NAutoCompleteV2
                      v-model="filters.tax_scheme"
                      :endpoint="`/api/company/${$route.params.company}/tax_scheme/choices`"
                      label="Tax Scheme"
                      fetch-on-mount
                    />
                  </div>
                  <div class="q-mx-sm">
                    <NAutoCompleteV2
                      v-model="filters.item_category"
                      :endpoint="`/api/company/${$route.params.company}/inventory-categories/choices`"
                      label="Item Category"
                      fetch-on-mount
                    />
                  </div>
                  <div class="q-mx-sm">
                    <SelectWithFetch
                      v-model="filters.item"
                      :endpoint="`/api/company/${$route.params.company}/items/purchase-choices/`"
                      label="Items"
                    />
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
                <div class="q-mx-md flex gap-4 q-mb-md q-mt-lg">
                  <q-btn
                    color="green"
                    label="Filter"
                    class="f-submit-btn"
                    @click="onFilterUpdate"
                  />
                  <q-btn
                    color="red"
                    icon="close"
                    class="f-reset-btn"
                    @click="resetFilters"
                  />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>

      <template #body-cell-voucher_id="props">
        <q-td :props="props">
          <div class="row align-center">
            <router-link
              v-if="checkPermissions('PurchaseVoucherView')"
              style="font-weight: 500; text-decoration: none"
              class="text-blue l-view-btn"
              :to="`/${$route.params.company}/purchase-voucher/${props.row.voucher_id}/view`"
            >
              {{ props.row.voucher_id }}
              {{ props.row.voucher__voucher_no }}
            </router-link>
            <span v-else>{{ props.row.voucher__voucher_no }}</span>
          </div>
        </q-td>
      </template>
      <template #body-cell-party_name="props">
        <q-td :props="props">
          <div
            v-if="props.row.customer_name"
            class="row align-center text-subtitle2 text-grey-8"
          >
            {{ props.row.customer_name }}
          </div>
          <div v-else>
            <q-icon name="domain" size="sm" class="text-grey-8" />
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{
              props.row.party_name
            }}</span>
          </div>
        </q-td>
      </template>
      <template #body-cell-voucher__date="props">
        <q-td :props="props">
          {{
            store.isCalendarInAD
              ? props.row.voucher__date
              : DateConverter.getRepresentation(props.row.voucher__date, 'bs')
          }}
        </q-td>
      </template>
    </q-table>
    <q-card v-if="aggregate" class="q-mt-md">
      <q-card-section>
        <div>
          <h5 class="q-ma-none q-ml-sm text-weight-bold text-grey-9">
            Aggregate Report for Filtered Data
          </h5>
        </div>
        <hr />
        <div class="q-mt-md">
          <div
            v-for="header in aggregate_headers"
            :key="header[0]"
            class="row q-mb-md"
          >
            <div class="col-6">
              <div class="text-weight-medium text-grey-9">
                {{ header[0] }}
              </div>
            </div>
            <div class="col-6">
              <div class="text-weight-bold">
                {{ parseInt((aggregate?.[header[1]] || 0).toFixed(2)) }}
              </div>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>
    <!-- {{ store.isCalendarInAD }} -->
  </div>
</template>

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
