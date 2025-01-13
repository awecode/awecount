<script setup>
import useList from '/src/composables/useList'

const endpoint = '/v1/items'
// console.log(useList(endpoint))
// export default {
//   setup() {
//     const endpoint = '/v1/category/'
//     return { ...useList(endpoint) }
//   },
// }
const { columns, rows, resetFilters, filters, loading, searchQuery, pagination, onRequest, confirmDeletion, initiallyLoaded } = useList(endpoint)
</script>

<template>
  <div class="q-pa-md">
    <div class="row">
      <q-btn
        class="q-ml-auto"
        color="green"
        icon-right="add"
        label="New Book"
        to="/book/add/"
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
      @request="onRequest"
    >
      <template #top>
        <div class="search-bar">
          <q-input
            v-model="searchQuery"
            dense
            class="search-bar-wrapper"
            debounce="500"
            placeholder="Search"
          >
            <template #append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="filterbtn">
            filters
          </q-btn>
        </div>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md">
            <q-btn color="blue" label="View" :to="`/inventory-account/detail/${props.row.id}/`" />
            <q-btn color="orange-6" label="Edit" :to="`/items/${props.row.id}/`" />
          </div>
          <!-- {{ props }} -->
        </q-td>
        <!-- TODO: add modals -->
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

.search-bar-wrapper {
  width: 100%;
}

.filterbtn {
  width: 100px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
