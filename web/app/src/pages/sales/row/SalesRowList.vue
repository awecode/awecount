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
          <q-btn class="filterbtn">
            <q-icon name="mdi-filter-variant"></q-icon>
            <q-menu>
              <div>
                <div class="q-mx-lg q-mt-md">
                  <h6 class="q-ma-none font-weight-bold text-grey-9">
                    Filters
                  </h6>
                </div>
                <hr />
                <div class="q-ma-md">
                  <div class="row q-col-gutter-md">
                    <!-- TODO: add Date Range -->
                    <q-input class="col-6 col-md-12" label="From Date">
                    </q-input>
                    <q-input class="col-6 col-md-12" label="To Date"> </q-input>
                  </div>
                  <q-select
                    label="Sales Agent"
                    v-model="filters.sales_agent"
                    :options="fetchedOptions[`sales-agent`]"
                    option-value="id"
                    option-label="name"
                    map-options
                    emit-value
                  />
                  <q-select
                    label="Party"
                    v-model="filters.parties"
                    :options="fetchedOptions.parties"
                    option-value="id"
                    option-label="name"
                    map-options
                    emit-value
                  />
                  <q-select
                    label="Tax Scheme"
                    v-model="filters.tax_scheme"
                    :options="fetchedOptions.tax_scheme"
                    option-value="id"
                    option-label="name"
                    map-options
                    emit-value
                  />
                  <q-select
                    label="Item Category"
                    v-model="filters.item_category"
                    :options="fetchedOptions[`inventory-categories`]"
                    option-value="id"
                    option-label="name"
                    map-options
                    emit-value
                  />
                  <q-select
                    label="Items"
                    v-model="filters.item"
                    :options="fetchedOptions.item_choices"
                    option-value="id"
                    option-label="name"
                    map-options
                    emit-value
                  />
                  <div class="q-my-md">
                    <div class="text-grey-8 text-subtitle2">
                      <strong>Statuses :</strong>
                    </div>
                    <MultiSelectChip
                      :options="[
                        'Draft',
                        'Issued',
                        'Paid',
                        'Partially Paid',
                        'Cancelled',
                      ]"
                      v-model="filters.status"
                    />
                    {{ filters.status }}
                    <div class="q-mt-md row q-gutter-x-md">
                      <q-btn
                        color="green"
                        label="Filter"
                        @click="onFilterUpdate"
                      ></q-btn>
                      <q-btn
                        color="red"
                        icon="close"
                        @click="resetFilters"
                      ></q-btn>
                    </div>
                  </div>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>

      <template v-slot:body-cell-voucher_id="props">
        <q-td :props="props">
          <div class="row align-center">
            <router-link
              style="font-weight: 500; text-decoration: none"
              class="text-blue"
              :to="`/sales-voucher/${props.row.voucher_id}/view`"
            >
              {{ props.row.voucher_id }}
            </router-link>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-party_name="props">
        <q-td :props="props">
          <div
            v-if="props.row.customer_name"
            class="row align-center text-subtitle2 text-grey-8"
          >
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
import MultiSelectChip from '/src/components/filter/MultiSelectChip.vue'
// import ListFilter from '/src/components/sales/row/ListFilter.vue'
import { Ref } from 'vue'
export default {
  setup() {
    const endpoint = '/v1/sales-row/'
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'voucher_id',
        label: 'Bill No',
        align: 'left',
        field: 'voucher_id',
        sortable: true,
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'voucher__date',
      },
      {
        name: 'buyers_name',
        label: 'Buyer',
        align: 'left',
        field: 'buyers_name',
      },
      {
        name: 'quantity',
        label: 'quantity',
        align: 'left',
        field: 'quantity',
      },
      {
        name: 'rate',
        label: 'Rate',
        align: 'left',
        field: 'rate',
      },
      {
        name: 'discount',
        label: 'Discount',
        align: 'left',
        field: 'discount_amount',
      },
      {
        name: 'tax_amount',
        label: 'Tax',
        align: 'left',
        field: 'tax_amount',
      },
      {
        name: 'net_amount',
        label: 'Amount',
        align: 'left',
        field: 'net_amount',
      },
    ]
    const usedOptions: Array<string> = [
      'sales-agent',
      'parties',
      'tax_scheme',
      'inventory-categories',
    ]
    const fetchedOptions: Ref<Record<string, Array<object> | null>> = ref({
      'sales-agent': null,
      parties: null,
      tax_scheme: null,
      'inventory-categories': null,
      item_choices: null,
    })
    return {
      ...listData,
      newColumn,
      usedOptions,
      fetchedOptions,
      MultiSelectChip,
    }
  },
  created() {
    this.usedOptions.forEach((type: string) => {
      useApi(`/v1/${type}/choices/`).then((data) => {
        this.fetchedOptions[type] = data
      })
      useApi('/v1/items/sales-choices/').then((data) => {
        this.fetchedOptions.item_choices = data
      })
    })
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
