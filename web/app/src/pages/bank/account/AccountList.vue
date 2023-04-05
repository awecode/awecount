<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn
        color="green"
        to="/bank-accounts/add/"
        label="New Account"
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
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            color="blue"
            class="q-py-none q-px-md font-size-sm q-mr-md"
            style="font-size: 12px"
            label="Account"
            :to="`/account/${props.row.id}/view/`"
          />
          <q-btn
            label="Edit"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm"
            style="font-size: 12px"
            :to="`/bank-accounts/${props.row.id}/`"
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
      title: 'Bank Accounts | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/bank-account/'
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'account_name',
        label: 'Account Name',
        align: 'left',
        field: 'account_name',
      },
      {
        name: 'account_number',
        label: 'Account Number',
        align: 'left',
        field: 'account_number',
      },
      {
        name: 'bankwallet_name',
        label: 'Bank/Wallet Name',
        align: 'left',
        field: 'account_name',
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
