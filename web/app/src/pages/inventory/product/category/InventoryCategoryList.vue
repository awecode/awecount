<template>
  <div class="q-pa-md">
    <div class="row justify-end" v-if="checkPermissions('CategoryCreate')">
      <q-btn color="green" to="/inventory-category/add/" label="New Category" class="q-ml-lg add-btn" icon-right="add" />
    </div>
    <q-table :rows="rows" :columns="newColumns" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
      row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn color="blue" class="q-py-none q-px-md font-size-sm" style="font-size: 12px" label="view"
            :to="`/account/${props.row.id}/view/`" />
        </q-td>
      </template>
      <template v-slot:body-cell-name="props">
        <q-td :props="props">
          <router-link v-if="checkPermissions('CategoryModify')" class="text-blue" style="text-decoration: none"
            :to="`/inventory-category/${props.row.id}/`">{{
              props.row.name }}</router-link>
          <span v-else>{{ props.row.name }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  setup() {
    const endpoint = '/v1/inventory-categories/'
    const metaData = {
      title: 'Inventory Category | Awecount',
    }
    useMeta(metaData)
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
    ]
    return { ...useList(endpoint), newColumns, checkPermissions }
  },
}
</script>
