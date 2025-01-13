<script setup>
import { useMeta } from 'quasar'
import checkPermissions from 'src/composables/checkPermissions'
import useList from '/src/composables/useList'

const endpoint = '/v1/items'
const metaData = {
  title: 'Items | Awecount',
}
useMeta(metaData)
const isItemImportOpen = ref(false)
const { columns, rows, loading, searchQuery, pagination, onRequest, filters, onFilterUpdate, resetFilters, loadData } = useList(endpoint)
</script>

<template>
  <div class="q-pa-md">
    <q-dialog v-model="isItemImportOpen">
      <q-card style="min-width: min(80vw, 900px)">
        <q-btn
          dense
          push
          round
          color="red"
          icon="close"
          style="position: absolute; right: 8px; top: 8px; z-index: 50"
          text-color="white"
          @click="isItemImportOpen = false"
        />
        <ItemImport
          @modal-close="isItemImportOpen = false"
          @update-list="
            isItemImportOpen = false
            loadData()
          "
        />
      </q-card>
    </q-dialog>
    <div v-if="checkPermissions('ItemCreate')" class="row justify-end q-gutter-md">
      <q-btn color="green" label="Import From XlS" @click="isItemImportOpen = true" />
      <q-btn
        class="add-btn"
        color="green"
        icon-right="add"
        label="Add Item"
        to="/items/add/"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      title="Income Items"
      :columns="columns"
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
                    <q-checkbox v-model="filters.can_be_purchased" label="Can be Purchased?" :false-value="null" />
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
                  <q-btn
                    class="f-submit-btn"
                    color="green"
                    label="Filter"
                    @click="onFilterUpdate"
                  />
                  <q-btn
                    class="f-reset-btn"
                    color="red"
                    icon="close"
                    @click="resetFilters"
                  />
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
            class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn"
            color="blue"
            label="View"
            style="font-size: 12px"
            :to="`/items/details/${props.row.id}/`"
          />
          <q-btn
            v-if="checkPermissions('ItemModify')"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn"
            color="orange-6"
            label="edit"
            style="font-size: 12px"
            :to="`/items/${props.row.id}/`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('ItemView')"
            class="text-blue"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/items/details/${props.row.id}/`"
          >
            {{ props.row.name }}
          </router-link>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
            {{ props.row.name }}
          </span>
        </q-td>
      </template>
      <template #body-cell-category="props">
        <q-td :props="props">
          <router-link
            v-if="props.row.category && checkPermissions('InventoryCategoryModify')"
            class="text-blue"
            style="font-weight: 500; text-decoration: none"
            :to="`/inventory-category/${props.row.category.id}/`"
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
