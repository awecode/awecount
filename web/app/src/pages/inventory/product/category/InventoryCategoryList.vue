<template>
  <div class="q-pa-md">
    <q-table
      title="Units"
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
          <!-- <q-btn icon="visibility" color="blue" dense flat to="" /> -->
          <q-btn
            color="blue"
            class="q-mr-md"
            label="View"
            :to="`/account/${props.row.id}/view/`"
          />
          <!-- <q-btn
            icon="delete"
            color="red"
            dense
            flat
            @click="confirmDeletion(props.row.id)"
          /> -->
          <!-- {{ props }} -->
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
    const endpoint = '/v1/inventory-account/';
    return { ...useList(endpoint) };
  },
};
</script>
