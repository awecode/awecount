<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn color="blue" label="Export" icon-right="download" />
      <q-btn color="green" to="/sales-voucher/add/" label="New Sales" icon-right="add" />
    </div>
    <q-table title="Income Items" :rows="rows" :columns="columns" :loading="loading" :filter="searchQuery"
      v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md">
      <template v-slot:top>
        <div class="search-bar">
          <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="search-bar-wrapper">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="filterbtn">filters</q-btn>
        </div>
      </template>
      <template v-slot:body-cell-actions="props">
        <!-- {{ props }} -->
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md">
            <q-btn color="blue" label="View" :to="`/sales-voucher/${props.row.voucher_no}/view/`" />
            <!-- <q-btn color="orange-6" label="Edit" :to="`/items/${props.row.id}/`" /> -->
          </div>
          <!-- {{ props }} -->
        </q-td>
        <!-- TODO: add modals -->
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList';
export default {
  setup() {
    const endpoint = '/v1/sales-voucher/';
    return { ...useList(endpoint) };
  },
};
// const {
//   columns,
//   rows,
//   resetFilters,
//   filters,
//   loading,
//   searchQuery,
//   pagination,
//   onRequest,
//   confirmDeletion,
//   initiallyLoaded,
// } = useList(endpoint);
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
