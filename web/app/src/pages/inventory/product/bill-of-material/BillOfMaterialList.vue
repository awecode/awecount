<template>
  <div class="q-pa-md">
    <div class="row justify-end q-gutter-md" v-if="checkPermissions('StockAdjustmentVoucherCreate')">
      <q-btn color="green" class="add-btn" to="/items/bill-of-material/add" label="Add Bill of Material"
        icon-right="add" />
    </div>
    <q-table title="Income Items" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery"
      v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <div class="search-bar">
          <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="w-full search-input">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
        </div>
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('BillOfMaterialModify')" color="orange-6"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn" style="font-size: 12px" label="edit"
            :to="`/items/bill-of-material/${props.row.id}/`" />
        </q-td>
      </template>

      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center">
            <div class="text-white text-subtitle row items-center justify-center" :class="props.row.status == 'Issued'
      ? 'bg-blue-2 text-blue-10'
      : props.row.status == 'Paid'
        ? 'bg-green-2 text-green-10'
        : props.row.status == 'Draft'
          ? 'bg-orange-2 text-orange-10'
          : props.row.status == 'Partially Paid'
            ? 'bg-green-1 text-green-6'
            : 'bg-red-2 text-red-10'
      " style="border-radius: 8px; padding: 2px 10px">
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script setup>
import useList from '/src/composables/useList'
import { useMeta } from 'quasar'
import checkPermissions from 'src/composables/checkPermissions'
const endpoint = '/v1/bill-of-material/'
const metaData = {
  title: 'Stock Adjustments | Awecount',
}
const newColumn = [
  {
    name: 'item',
    label: 'Item',
    align: 'left',
    field: 'item',
    sortable: true,
  },
  { name: 'actions', align: 'left', label: 'Actions' },
]
useMeta(metaData)
const {
  rows,
  loading,
  searchQuery,
  pagination,
  onRequest
} = useList(endpoint)
</script>

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
