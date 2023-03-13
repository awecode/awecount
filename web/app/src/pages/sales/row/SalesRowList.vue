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
          <q-btn class="filterbtn">filters</q-btn>
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
  </div>
</template>

<script>
import useList from '/src/composables/useList'
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

    return { ...listData, newColumn }
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
