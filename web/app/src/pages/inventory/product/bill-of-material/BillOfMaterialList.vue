<script setup>
import { useMeta } from 'quasar'
import checkPermissions from 'src/composables/checkPermissions'
import useList from '/src/composables/useList'

const endpoint = '/v1/bill-of-material/'
const metaData = {
  title: 'Inventory Adjustments | Awecount',
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
const { rows, loading, searchQuery, pagination, onRequest } = useList(endpoint)
</script>

<template>
  <div class="q-pa-md">
    <div v-if="checkPermissions('BillOfMaterialCreate')" class="row justify-end q-gutter-md">
      <q-btn
        class="add-btn"
        color="green"
        icon-right="add"
        label="Add Bill of Material"
        to="/items/bill-of-material/add"
      />
    </div>
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
        <div class="search-bar">
          <q-input
            v-model="searchQuery"
            dense
            class="w-full search-input"
            debounce="500"
            placeholder="Search"
          >
            <template #append>
              <q-icon name="search" />
            </template>
          </q-input>
        </div>
      </template>

      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('BillOfMaterialModify')"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn"
            color="orange-6"
            label="edit"
            style="font-size: 12px"
            :to="`/items/bill-of-material/${props.row.id}/`"
          />
        </q-td>
      </template>

      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center">
            <div
              class="text-white text-subtitle row items-center justify-center"
              style="border-radius: 8px; padding: 2px 10px"
              :class="
                props.row.status == 'Issued' ? 'bg-blue-2 text-blue-10'
                : props.row.status == 'Paid' ? 'bg-green-2 text-green-10'
                  : props.row.status == 'Draft' ? 'bg-orange-2 text-orange-10'
                    : props.row.status == 'Partially Paid' ? 'bg-green-1 text-green-6'
                      : 'bg-red-2 text-red-10'
              "
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
