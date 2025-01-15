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
      <q-btn
        v-if="checkPermissions('category.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New Category"
        :to="`/${$route.params.company}/account-category/create/`"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      title="Income Items"
      :columns="newColumns"
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
            class="full-width search-input"
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
                  <div class="q-pb-sm">
                    <q-checkbox v-model="filters.default" label="Is Default?" :false-value="null" />
                  </div>
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md">
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
            v-if="checkPermissions('category.modify')"
            class="q-py-none q-px-md font-size-sm l-edit-btn"
            color="orange-7"
            label="Edit"
            style="font-size: 12px"
            :to="`/${$route.params.company}/account-category/${props.row.id}/`"
          />
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
