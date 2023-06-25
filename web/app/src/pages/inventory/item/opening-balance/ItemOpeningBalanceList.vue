<template>
  <div class="q-pa-md">
    <div class="row" v-if="checkPermissions('AccountOpeningBalanceCreate')">
      <q-btn color="green" to="/items/opening/add" label="New Opening Balance" class="q-ml-auto" icon-right="add" />
    </div>
    <q-table :rows="rows" :columns="newColumns" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
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
          <q-btn v-if="checkPermissions('AccountOpeningBalanceModify')" color="orange-6"
            class="q-py-none q-px-md font-size-sm" style="font-size: 12px" label="EDIT"
            :to="`/items/opening/${props.row.id}/`" />
        </q-td>
      </template>
      <template v-slot:body-cell-name="props">
        <q-td :props="props">
          <router-link v-if="checkPermissions('ItemModify')" style="font-weight: 500; text-decoration: none"
            class="text-blue" :to="`/items/${props.row.item_id}/`">{{
              props.row.name
            }}</router-link>
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
    const endpoint = '/v1/item-opening-balance/'
    const metaData = {
      title: 'Stock Opening | Awecount',
    }
    const newColumns = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
      },
      {
        name: 'balance',
        label: 'Opening Balance',
        align: 'left',
        field: 'opening_balance',
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'left',
      },
    ]
    useMeta(metaData)
    return { ...useList(endpoint), checkPermissions, newColumns }
  },
}
</script>
