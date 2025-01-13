<script>
export default {
  setup() {
    const metaData = {
      title: 'Tax Schemes | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/tax_scheme/`
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
        sortable: true,
      },
      {
        name: 'short_name',
        label: 'Short Name',
        align: 'left',
        field: 'short_name',
        sortable: true,
      },
      {
        name: 'rate',
        label: 'Rate',
        align: 'left',
        field: 'rate',
        sortable: true,
      },
      {
        name: 'recoverable',
        label: 'Recoverable',
        align: 'center',
        field: 'recoverable',
        sortable: true,
      },
      {
        name: 'default',
        label: 'Default',
        align: 'center',
        field: 'default',
        sortable: true,
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    return { ...listData, newColumn, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn v-if="checkPermissions('taxscheme.create')" color="green" :to="`/${$route.params.company}/taxes/create/`" label="New Tax Scheme" class="add-btn" icon-right="add" />
    </div>

    <q-table v-model:pagination="pagination" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" row-key="id" class="q-mt-md" :rows-per-page-options="[20]" @request="onRequest">
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link v-if="checkPermissions('taxscheme.modify')" :to="`/${$route.params.company}/taxes/${props.row.id}/`" style="text-decoration: none" class="text-blue">
            {{ props.row.name }}
          </router-link>
          <span v-else>{{ props.row.name }}</span>
        </q-td>
      </template>
      <template #body-cell-recoverable="props">
        <q-td :props="props">
          <ShowListBoolean :value="props.row.recoverable" />
        </q-td>
      </template>
      <template #body-cell-default="props">
        <q-td :props="props">
          <ShowListBoolean :value="props.row.default" />
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn color="orange" class="q-py-none q-px-md font-size-sm l-edit-btn" style="font-size: 12px" label="Edit" :to="`/${$route.params.company}/taxes/${props.row.id}/`" />
        </q-td>
      </template>
      <template #body-cell-bankwallet_name="props">
        <q-td :props="props">
          {{ props.row.is_wallet ? props.row.wallet_name : props.row.bank_name }}
        </q-td>
      </template>
    </q-table>
  </div>
</template>
