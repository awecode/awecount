<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn v-if="checkPermissions('CategoryCreate')" color="green" to="/account-category/add/" label="New Category"
        class="add-btn" icon-right="add" />
    </div>
    <q-table title="Income Items" :rows="rows" :columns="newColumns" :loading="loading" :filter="searchQuery"
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
              <div class="menu-wrapper" style="width: min(300px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-pb-sm">
                    <q-checkbox v-model="filters.default" label="Is Default?" :false-value="null"></q-checkbox>
                  </div>
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md">
                  <q-btn color="green" label="Filter" class="f-submit-btn" @click="onFilterUpdate"></q-btn>
                  <q-btn color="red" icon="close" class="f-reset-btn" @click="resetFilters"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('CategoryModify')" color="orange-7" label="Edit"
            :to="`/account-category/${props.row.id}/`" class="q-py-none q-px-md font-size-sm l-edit-btn" style="font-size: 12px" />
          <!-- {{ props }} -->
        </q-td>
        <!-- TODO: add modals -->
      </template>
      <template v-slot:body-cell-default="props">
        <q-td :props="props">
          <q-checkbox v-model="props.row.default" color="grey" disable>
          </q-checkbox>
        </q-td>
        <!-- TODO: add modals -->
      </template>
    </q-table>
  </div>
</template>

<script setup>
import checkPermissions from 'src/composables/checkPermissions'
const metaData = {
  title: 'Account Categories | Awecount',
}
useMeta(metaData)
const endpoint = '/v1/categories/'
const newColumns = [
  {
    name: 'code',
    label: 'Code.',
    align: 'left',
    field: 'code',
    sortable: true
  },
  {
    name: 'name',
    label: 'Name',
    align: 'left',
    field: 'name',
    sortable: true
  },
  { name: 'default', label: 'Default', align: 'center', field: 'default', sortable: true},
  { name: 'actions', label: 'Actions', align: 'center' },
]
const {
  rows,
  resetFilters,
  filters,
  loading,
  searchQuery,
  pagination,
  onRequest,
  onFilterUpdate,
} = useList(endpoint)
</script>
