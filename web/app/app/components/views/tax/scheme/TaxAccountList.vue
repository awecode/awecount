<script>
export default {
  setup() {
    const metaData = {
      title: 'Tax Schemes | Awecount',
    }
    useHead(metaData)
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
      <q-btn
        v-if="checkPermissions('taxscheme.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New Tax Scheme"
        :to="`/${$route.params.company}/tax/schemes/create`"
      />
    </div>

    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      :columns="newColumn"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('taxscheme.update')"
            class="text-blue"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/tax/schemes/${props.row.id}`"
          >
            {{ props.row.name }}
          </router-link>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
            {{ props.row.name }}
          </span>
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
          <q-btn
            class="q-py-none q-px-md font-size-sm l-edit-btn"
            color="orange"
            label="Edit"
            style="font-size: 12px"
            :to="`/${$route.params.company}/tax/schemes/${props.row.id}/edit`"
          />
        </q-td>
      </template>
      <template #body-cell-bankwallet_name="props">
        <q-td :props="props">
          {{ props.row.is_wallet ? props.row.wallet_name : props.row.bank_name }}
        </q-td>
      </template>
      <template #body-cell-rate="props">
        <q-td :props="props">
          <FormattedNumber type="unit" unit="percent" :value="props.row.rate" />
        </q-td>
      </template>
    </q-table>
  </div>
</template>
