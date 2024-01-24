<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end" v-if="checkPermissions('SalesDiscountDelete')">
      <q-btn color="green" to="/sales-discount/add/" label="New sales discount" icon-right="add" class="add-btn" />
    </div>
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
                  <div class="q-ma-sm">
                    <MultiSelectChip v-model="filters.type" :options="['Percent', 'Amount']" />
                  </div>
                  <div class="q-mt-md">
                    <q-checkbox v-model="filters.trade_discount" label="Is Trade Discount?"
                      :false-value="null"></q-checkbox>
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

      <template v-slot:body-cell-trade_discount="props">
        <q-td :props="props">
          <div class="row align-center text-subtitle2 text-grey-8 justify-center">
            <q-checkbox disable v-model="props.row.trade_discount" color="grey"></q-checkbox>
            <!-- {{ props.row.trade_discount }} -->
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <q-btn v-if="checkPermissions('SalesDiscountModify')" color="orange-6" label="Edit"
            class="q-py-none q-px-md font-size-sm l-edit-btn" style="font-size: 12px" :to="`/sales-discount/${props.row.id}/`" />
        </q-td>
      </template>
      <template v-slot:body-cell-name="props">
        <q-td :props="props">
          <router-link v-if="checkPermissions('SalesDiscountModify')" :to="`/sales-discount/${props.row.id}/`"
            style="font-weight: 500; text-decoration: none" class="text-blue">
            {{ props.row.name }}
          </router-link>
          <span v-else>{{ props.row.name }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  setup() {
    const metaData = {
      title: 'Sales Discounts | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/sales-discount/'
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
        sortable: true
      },
      { name: 'type', label: 'Type', align: 'left', field: 'type', sortable: true},
      {
        name: 'value',
        label: 'Value',
        align: 'left',
        field: 'value',
        sortable: true
      },
      {
        name: 'trade_discount',
        label: 'Trade Discount',
        align: 'center',
        field: 'trade_discount',
        sortable: true
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'left',
        field: 'actions',
      },
    ]

    return { ...listData, newColumn, checkPermissions }
  },
}
</script>
