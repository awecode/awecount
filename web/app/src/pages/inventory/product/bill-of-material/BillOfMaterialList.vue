<script setup>
import { useMeta } from 'quasar'
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

const route = useRoute()
const endpoint = `/api/company/${route.params.company}/bill-of-material/`
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
const {
  rows,
  loading,
  searchQuery,
  pagination,
  onRequest,
} = useList(endpoint)
</script>

<template>
  <div class="q-pa-md">
    <div v-if="checkPermissions('BillOfMaterialCreate')" class="row justify-end q-gutter-md">
      <q-btn
        color="green"
        class="add-btn"
        :to="`/${$route.params.company}/items/bill-of-material/add`"
        label="Add Bill of Material"
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
        </div>
      </template>

      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('BillOfMaterialModify')"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn"
            style="font-size: 12px"
            label="edit"
            :to="`/${$route.params.company}/items/bill-of-material/${props.row.id}/`"
          />
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
