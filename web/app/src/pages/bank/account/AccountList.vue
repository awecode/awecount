<script>
export default {
  setup() {
    const metaData = {
      title: 'Bank Accounts | Awecount',
    }
    const route = useRoute()
    useMeta(metaData)
    const endpoint = `/api/company/${route.params.company}/bank-account/`
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'account_name',
        label: 'Account Name',
        align: 'left',
        field: 'account_name',
        style: 'text-wrap: wrap;',
      },
      {
        name: 'account_number',
        label: 'Account Number',
        align: 'left',
        field: 'account_number',
        style: 'text-wrap: wrap;',
      },
      {
        name: 'bank_name',
        label: 'Bank/Wallet Name',
        align: 'left',
        field: 'bank_name',
        style: 'text-wrap: wrap;',
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
  <div class="q-pa-md w-full">
    <div class="row justify-end">
      <q-btn
        v-if="checkPermissions('BankAccountCreate')"
        color="green"
        :to="`/${$route.params.company}/bank-accounts/add/`"
        label="New Account"
        class="q-ml-lg add-btn"
        icon-right="add"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      :rows="rows"
      :columns="newColumn"
      :loading="loading"
      :filter="searchQuery"
      row-key="id"
      class="q-mt-md"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            color="blue"
            class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn"
            style="font-size: 12px"
            label="Account"
            :to="`/${$route.params.company}/account/${props.row.ledger}/view/`"
          />
          <q-btn
            v-if="checkPermissions('BankAccountModify')"
            label="Edit"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm l-edit-btn"
            style="font-size: 12px"
            :to="`/${$route.params.company}/bank-accounts/${props.row.id}/`"
          />
        </q-td>
      </template>
    </q-table>
  </div>
</template>
