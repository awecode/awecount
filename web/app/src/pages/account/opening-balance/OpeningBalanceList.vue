<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn v-if="checkPermissions('AccountOpeningBalanceCreate')" color="green" to="/account-opening-balance/add/"
        label="New Opening Balance" class="add-btn" icon-right="add" />
    </div>
    <q-table title="Opening Balances" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery"
      v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="full-width search-input">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('AccountOpeningBalanceModify')" label="Edit" color="orange-6"
            class="q-py-none q-px-md font-size-sm l-edit-btn" style="font-size: 12px"
            :to="`/account-opening-balance/${props.row.id}/`" />
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
export default {
  setup() {
    const metaData = {
      title: 'Account Opening Balances | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/account-opening-balance/'
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
      },
      {
        name: 'opening_dr',
        label: 'Opening Dr',
        align: 'left',
        field: 'opening_dr',
        sortable: true
      },
      {
        name: 'opening_cr',
        label: 'Opening Cr',
        align: 'left',
        field: 'opening_cr',
        sortable: true
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    return { ...useList(endpoint), newColumn, checkPermissions }
  },
}
</script>
