<script setup>
import { useMeta } from 'quasar'
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

const route = useRoute()
const endpoint = `/api/company/${route.params.company}/inventory-conversion/`
const metaData = {
  title: 'Inventory Conversion | Awecount',
}
useMeta(metaData)
const {
  rows,
  loading,
  searchQuery,
  pagination,
  onRequest,
  filters,
  onFilterUpdate,
  resetFilters,
} = useList(endpoint)
const newColumn = [
  {
    name: 'voucher_no',
    label: 'Voucher no',
    align: 'left',
    field: 'voucher_no',
    sortable: true,
  },
  {
    name: 'date',
    label: 'Date',
    align: 'left',
    field: 'date',
    sortable: true,
  },
  {
    name: 'status',
    label: 'Status',
    align: 'center',
    field: 'status',
    sortable: true,
  },
  { name: 'actions', align: 'left', label: 'Actions' },
]
</script>

<template>
  <div class="q-pa-md">
    <div v-if="checkPermissions('InventoryConversionVoucherCreate')" class="row justify-end q-gutter-md">
      <q-btn
        color="green"
        class="add-btn"
        to="/items/inventory-conversion/add"
        label="Add Inventory Conversion Voucher"
        icon-right="add"
      />
    </div>
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
          <q-input v-model="searchQuery" dense debounce="500" placeholder="Search" class="w-full search-input">
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
                  <div class="q-ma-sm">
                    <MultiSelectChip v-model="filters.status" :options="['Issued', 'Cancelled']" />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:start-date="filters.start_date" v-model:end-date="filters.end_date" />
                </div>
                <div class="q-mx-md row q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="q-mr-md f-submit-btn" @click="onFilterUpdate" />
                  <q-btn color="red" icon="close" class="f-reset-btn" @click="resetFilters" />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>

      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('InventoryConversionVoucherView')"
            color="blue-6"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn"
            style="font-size: 12px"
            label="View"
            :to="`/items/inventory-conversion/${props.row.id}/view`"
          />
          <q-btn
            v-if="checkPermissions('InventoryConversionVoucherModify')"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn"
            style="font-size: 12px"
            label="edit"
            :to="`/items/inventory-conversion/${props.row.id}/`"
          />
        </q-td>
      </template>

      <template #body-cell-voucher_no="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('InventoryConversionVoucherModify')"
            :to="`/items/inventory-conversion/${props.row.id}/`"
            style="font-weight: 500; text-decoration: none"
            class="text-blue"
          >
            {{ props.row.voucher_no }}
          </router-link>
          <span v-else>{{ props.row.voucher_no }}</span>
        </q-td>
      </template>

      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center">
            <div
              class="text-white text-subtitle row items-center justify-center"
              :class="props.row.status == 'Issued'
                ? 'bg-blue-2 text-blue-10'
                : props.row.status == 'Paid'
                  ? 'bg-green-2 text-green-10'
                  : props.row.status == 'Draft'
                    ? 'bg-orange-2 text-orange-10'
                    : props.row.status == 'Partially Paid'
                      ? 'bg-green-1 text-green-6'
                      : 'bg-red-2 text-red-10'
              "
              style="border-radius: 8px; padding: 2px 10px"
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<style>
.search-bar {
  display: flex;
  width: 100%;
  column-gap: 20px;
}

.f-open-btn {
  width: 80px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
