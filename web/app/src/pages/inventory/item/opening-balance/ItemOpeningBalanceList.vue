<template>
  <div class="q-pa-md">
    <div class="row">
      <q-btn
        color="green"
        to="/items/opening/add"
        label="New Opening Balance"
        class="q-ml-auto"
        icon-right="add"
      />
    </div>
    <q-table
      title="Stock Opening Balances"
      :rows="rows"
      :columns="columns"
      :loading="loading"
      :filter="searchQuery"
      v-model:pagination="pagination"
      row-key="id"
      @request="onRequest"
      class="q-mt-md"
    >
      <template v-slot:top-right>
        <q-input
          dense
          debounce="500"
          v-model="searchQuery"
          placeholder="Search"
        >
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            color="orange-6"
            class="q-mr-md"
            label="EDIT"
            :to="`/items/opening/${props.row.item_id}/`"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-category="props">
        <q-td :props="props">
          <router-link
            :to="`/account/category/${props.row.category.id}/edit/`"
            >{{ props.row.category.name }}</router-link
          >
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList';
export default {
  setup() {
    const endpoint = '/v1/item-opening-balance/';
    return { ...useList(endpoint) };
  },
};
</script>
