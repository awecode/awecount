<template>
  <div class="q-pa-md">
    <q-table :rows="rows" :columns="columnList" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
      row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="full-width">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('InventoryAccountView')" color="blue" class="q-py-none q-px-md font-size-sm"
            style="font-size: 12px" label="view" :to="`/inventory-account/detail/${props.row.id}`" />
        </q-td>
      </template>
      <template v-slot:body-cell-category="props">
        <q-td :props="props">
          <router-link :to="`/account/category/${props.row.category.id}/edit/`">{{ props.row.category.name
          }}</router-link>
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
    const endpoint = '/v1/inventory-account/'
    const columnList = [
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
      {
        name: 'opening_balance',
        label: 'Opening Balance',
        align: 'left',
        field: 'opening_balance',
      },
      {
        name: 'current_balance',
        label: 'Current Balance',
        align: 'left',
        field: 'current_balance',
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'left',
      },
    ]
    const metaData = {
      title: 'Inventory Accounts | Awecount',
    }
    useMeta(metaData)
    return { ...useList(endpoint), columnList, checkPermissions }
  },
}
</script>
