<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn
        color="green"
        to="/taxes/add/"
        label="New Tax Scheme"
        class="q-ml-lg"
        icon-right="add"
      />
    </div>

    <q-table
      :rows="rows"
      :columns="newColumn"
      :loading="loading"
      :filter="searchQuery"
      v-model:pagination="pagination"
      row-key="id"
      @request="onRequest"
      class="q-mt-md"
      :rows-per-page-options="[20]"
    >
      <template v-slot:body-cell-name="props">
        <q-td :props="props">
          <router-link
            :to="`/taxes/${props.row.id}/`"
            style="text-decoration: none"
            class="text-blue"
          >
            {{ props.row.name }}
          </router-link>
        </q-td>
      </template>
      <template v-slot:body-cell-recoverable="props">
        <q-td :props="props">
          <q-checkbox
            color="grey-6"
            v-model="props.row.recoverable"
            disable
          ></q-checkbox>
        </q-td>
      </template>
      <template v-slot:body-cell-default="props">
        <q-td :props="props">
          <q-checkbox
            color="grey-6"
            v-model="props.row.default"
            disable
          ></q-checkbox>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            color="blue"
            class="q-py-none q-px-md font-size-sm"
            style="font-size: 12px"
            label="Tax Account"
            :to="`/taxes/account/${props.row.id}/`"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-bankwallet_name="props">
        <q-td :props="props">
          {{
            props.row.is_wallet ? props.row.wallet_name : props.row.bank_name
          }}
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
export default {
  setup() {
    const metaData = {
      title: 'Tax Schemes | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/tax_scheme/'
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
      },
      {
        name: 'short_name',
        label: 'Short Name',
        align: 'left',
        field: 'short_name',
      },
      {
        name: 'rate',
        label: 'Rate',
        align: 'left',
        field: 'rate',
      },
      {
        name: 'recoverable',
        label: 'Recoverable',
        align: 'center',
        field: 'recoverable',
      },
      {
        name: 'default',
        label: 'Default',
        align: 'center',
        field: 'default',
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    return { ...listData, newColumn }
  },
}
</script>
