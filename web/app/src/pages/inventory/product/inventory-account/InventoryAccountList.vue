<template>
  <div class="q-pa-md">
    <q-table :rows="rows" :columns="columnList" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
      row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="full-width search-input">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('InventoryAccountView')" color="blue"
            class="q-py-none q-px-md font-size-sm l-view-btn" style="font-size: 12px" label="view"
            :to="`/inventory-account/detail/${props.row.id}`" />
        </q-td>
      </template>
      <template v-slot:body-cell-name="props">
        <q-td :props="props" style="padding: 0;">
          <router-link v-if="checkPermissions('InventoryAccountView')" :to="`/inventory-account/detail/${props.row.id}`"
            style="text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px;"
            class="text-blue font-medium">
            {{ props.row.name }}
          </router-link>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px;">
            {{ props.row.name }}
          </span>
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
        name: 'code',
        label: 'Code.',
        align: 'left',
        field: 'code',
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
