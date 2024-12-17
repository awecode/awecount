<script setup>
import { useMeta } from 'quasar'
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

const route = useRoute()
const endpoint = `/api/company/${route.params.company}/items`
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
  loadData,
} = useList(endpoint)
</script>

<template>
  <div class="q-pa-md">
    <q-dialog v-model="isItemImportOpen">
      <q-card style="min-width: min(80vw, 900px)">
        <q-btn
          style="position: absolute; right: 8px; top: 8px; z-index: 50"
          push
          color="red"
          text-color="white"
          round
          dense
          icon="close"
          @click="isItemImportOpen = false"
        />
        <ItemImport @modal-close="isItemImportOpen = false" @update-list="isItemImportOpen = false; loadData();" />
      </q-card>
    </q-dialog>
    <div v-if="checkPermissions('ItemCreate')" class="row justify-end q-gutter-md">
      <q-btn color="green" label="Import From XlS" @click="isItemImportOpen = true" />
      <q-btn color="green" class="add-btn" to="/items/add/" label="Add Item" icon-right="add" />
    </div>
    <q-table
      v-model:pagination="pagination"
      title="Income Items"
      :rows="rows"
      :columns="columns"
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
              <div class="menu-wrapper" style="width: min(300px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">
                    Filters
                  </h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mb-sm">
                    <q-checkbox v-model="filters.can_be_sold" label="Can be Sold?" :false-value="null" />
                  </div>
                  <div>
                    <q-checkbox
                      v-model="filters.can_be_purchased"
                      label="Can be Purchased?"
                      :false-value="null"
                    />
                  </div>
                  <div class="q-mx-sm">
                    <n-auto-complete-v2
                      v-model="filters.category"
                      endpoint="v1/inventory-categories/choices/"
                      label="Category"
                      :fetch-on-mount="true"
                    />
                  </div>
                </div>
                <div class="q-mx-md row q-gutter-md q-mb-md">
                  <q-btn color="green" class="f-submit-btn" label="Filter" @click="onFilterUpdate" />
                  <q-btn color="red" class="f-reset-btn" icon="close" @click="resetFilters" />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('ItemView')"
            color="blue"
            class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn"
            style="font-size: 12px"
            label="View"
            :to="`/items/details/${props.row.id}/`"
          />
          <q-btn
            v-if="checkPermissions('ItemModify')"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn"
            style="font-size: 12px"
            label="edit"
            :to="`/items/${props.row.id}/`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('ItemView')"
            :to="`/items/details/${props.row.id}/`"
            style="font-weight: 500; text-decoration: none"
            class="text-blue"
          >
            {{ props.row.name }}
          </router-link>
          <span v-else>{{ props.row.name }}</span>
        </q-td>
      </template>
      <template #body-cell-category="props">
        <q-td :props="props">
          <router-link
            v-if="props.row.category && checkPermissions('InventoryCategoryModify')"
            :to="`/inventory-category/${props.row.category.id}/`"
            style="font-weight: 500; text-decoration: none"
            class="text-blue"
          >
            {{ props.row.category?.name }}
          </router-link>
          <span v-else>{{ props.row.category?.name }}</span>
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
