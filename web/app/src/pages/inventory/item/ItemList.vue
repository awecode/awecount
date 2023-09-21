<template>
  <div class="q-pa-md">
    <q-dialog v-model="isItemImportOpen">
      <q-card style="min-width: 80vw">
        <ItemImport @modalClose="isItemImportOpen = false"></ItemImport>
      </q-card>
    </q-dialog>
    <div class="row" v-if="checkPermissions('ItemCreate')">
      <q-btn color="blue" label="Import From XlS" @click="isItemImportOpen = true"></q-btn>
      <q-btn color="green" to="/items/add/" label="Add Item" class="q-ml-auto" icon-right="add" />
    </div>
    <q-table title="Income Items" :rows="rows" :columns="columns" :loading="loading" :filter="searchQuery"
      v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <div class="search-bar">
          <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="search-bar-wrapper">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="filterbtn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(300px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mb-sm">
                    <q-checkbox v-model="filters.can_be_sold" label="Can be Sold?" :false-value="null"></q-checkbox>
                  </div>
                  <div>
                    <q-checkbox v-model="filters.can_be_purchased" label="Can be Purchased?"
                      :false-value="null"></q-checkbox>
                  </div>
                  <div class="q-mx-sm">
                    <SelectWithFetch v-model="filters.category" endpoint="v1/inventory-categories/choices/"
                      label="Category" />
                  </div>
                </div>
                <div class="q-mx-md row q-gutter-md q-mb-md">
                  <q-btn color="green" label="Filter" @click="onFilterUpdate"></q-btn>
                  <q-btn color="red" icon="close" @click="resetFilters"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('ItemView')" color="blue" class="q-py-none q-px-md font-size-sm q-mr-md"
            style="font-size: 12px" label="View" :to="`/items/details/${props.row.id}/`" />
          <q-btn v-if="checkPermissions('ItemModify')" color="orange-6" class="q-py-none q-px-md font-size-sm q-mr-sm"
            style="font-size: 12px" label="edit" :to="`/items/${props.row.id}/`" />
        </q-td>
        <!-- TODO: add modals -->
      </template>
      <template v-slot:body-cell-category="props">
        <q-td :props="props">
          <router-link v-if="props.row.category && checkPermissions('InventoryCategoryModify')"
            :to="`/inventory-category/${props.row.category.id}/`" style="font-weight: 500; text-decoration: none"
            class="text-blue">
            {{ props.row.category?.name }}
          </router-link>
          <span v-else>{{ props.row.category?.name }}</span>
        </q-td>
        <!-- TODO: add modals -->
      </template>
    </q-table>
  </div>
</template>

<script setup>
import useList from '/src/composables/useList'
import { useMeta } from 'quasar'
import checkPermissions from 'src/composables/checkPermissions'
const endpoint = '/v1/items'
// console.log(useList(endpoint))
// export default {
//   setup() {
//     const endpoint = '/v1/category/'
//     return { ...useList(endpoint) }
//   },
// }
const metaData = {
  title: 'Items | Awecount',
}
useMeta(metaData)
const isItemImportOpen = ref(false)
const {
  columns,
  rows,
  loading,
  searchQuery,
  pagination,
  onRequest,
  filters,
  onFilterUpdate,
  resetFilters,
} = useList(endpoint)
// filters.value.can_be_sold = false
// filters.value.can_be_purchased = false
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
  width: 80px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
