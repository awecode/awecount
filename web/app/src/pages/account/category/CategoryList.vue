<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn
        color="green"
        to="/account/category/add/"
        label="New Category"
        class="q-ml-lg"
        icon-right="add"
      />
    </div>
    <q-table
      title="Income Items"
      :rows="rows"
      :columns="newColumns"
      :loading="loading"
      :filter="searchQuery"
      v-model:pagination="pagination"
      row-key="id"
      @request="onRequest"
      class="q-mt-md"
      :rows-per-page-options="[20]"
    >
      <template v-slot:top>
        <div class="search-bar">
          <q-input
            dense
            debounce="500"
            v-model="searchQuery"
            placeholder="Search"
            class="search-bar-wrapper"
          >
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="filterbtn">filters</q-btn>
        </div>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            color="orange-7"
            label="Edit"
            :to="`/income/item/${props.row.id}/edit/`"
            class="q-py-none q-px-md font-size-sm"
            style="font-size: 12px"
          />
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
import useList from '/src/composables/useList'
const endpoint = '/v1/categories/'
const newColumns = [
  {
    name: 'code',
    label: 'Code.',
    align: 'left',
    field: 'code',
  },
  {
    name: 'name',
    label: 'Name',
    align: 'left',
    field: 'name',
  },
  { name: 'default', label: 'Default', align: 'center', field: 'default' },
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
} = useList(endpoint)
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
  width: 100px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
