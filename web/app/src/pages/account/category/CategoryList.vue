<script setup>
import checkPermissions from 'src/composables/checkPermissions'

const metaData = {
  title: 'Account Categories | Awecount',
}
const route = useRoute()
useMeta(metaData)
const endpoint = `/api/company/${route.params.company}/categories/`
const newColumns = [
  {
    name: 'code',
    label: 'Code.',
    align: 'left',
    field: 'code',
    sortable: true,
  },
  {
    name: 'name',
    label: 'Name',
    align: 'left',
    field: 'name',
    sortable: true,
  },
  { name: 'default', label: 'Default', align: 'center', field: 'default', sortable: true },
  { name: 'actions', label: 'Actions', align: 'center' },
]
const { rows, resetFilters, filters, loading, searchQuery, pagination, onRequest, onFilterUpdate } = useList(endpoint)
</script>

<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn v-if="checkPermissions('category.create')" color="green" :to="`/${$route.params.company}/account-category/create/`" label="New Category" class="add-btn" icon-right="add" />
    </div>
    <q-table v-model:pagination="pagination" title="Income Items" :rows="rows" :columns="newColumns" :loading="loading" :filter="searchQuery" row-key="id" class="q-mt-md" :rows-per-page-options="[20]" @request="onRequest">
      <template #top>
        <div class="search-bar">
          <q-input v-model="searchQuery" dense debounce="500" placeholder="Search" class="full-width search-input">
            <template #append>
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
                    <q-checkbox v-model="filters.default" label="Is Default?" :false-value="null" />
                  </div>
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md">
                  <q-btn color="green" label="Filter" class="f-submit-btn" @click="onFilterUpdate" />
                  <q-btn color="red" icon="close" class="f-reset-btn" @click="resetFilters" />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('category.modify')" color="orange-7" label="Edit" :to="`/${$route.params.company}/account-category/${props.row.id}/`" class="q-py-none q-px-md font-size-sm l-edit-btn" style="font-size: 12px" />
        </q-td>
      </template>
      <template #body-cell-default="props">
        <q-td :props="props">
          <ShowListBoolean :value="props.row.default" />
        </q-td>
      </template>
    </q-table>
  </div>
</template>
