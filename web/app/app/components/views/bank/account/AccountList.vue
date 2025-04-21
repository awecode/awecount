<script>
export default defineNuxtComponent({
  setup() {
    const metaData = {
      title: 'Bank Accounts | Awecount',
    }
    const route = useRoute()
    useHead(metaData)
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
})
</script>

<template>
  <div class="q-pa-md w-full">
    <div class="row justify-end">
      <q-btn
        v-if="checkPermissions('bankaccount.create')"
        class="q-ml-lg add-btn"
        color="green"
        icon-right="add"
        label="New Account"
        :to="`/${$route.params.company}/banking/bank-accounts/create`"
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
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn"
            color="blue"
            label="Account"
            style="font-size: 12px"
            :to="`/${$route.params.company}/account/ledgers/${props.row.ledger}`"
          />
          <q-btn
            v-if="checkPermissions('bankaccount.update')"
            class="q-py-none q-px-md font-size-sm l-edit-btn"
            color="orange-6"
            label="Edit"
            style="font-size: 12px"
            :to="`/${$route.params.company}/banking/bank-accounts/${props.row.id}/edit`"
          />
        </q-td>
      </template>
    </q-table>
  </div>
</template>
