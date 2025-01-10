<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn v-if="checkPermissions('PaymentModeCreate')" color="green" to="/settings/payment-mode/add/"
        label="New Payment Mode" icon-right="add" class="add-btn" />
    </div>
    <q-table :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
      row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md">
            <q-btn class="q-py-none q-px-md font-size-sm" style="font-size: 12px" color="blue l-view-btn" label="Edit"
              :to="`/settings/payment-mode/${props.row.id}/`" />
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
export default {
  setup() {
    const metaData = {
      title: 'Payment Modes | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/payment-modes/'
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
      },
      { name: 'actions', label: 'Actions', align: 'left' },
    ]

    return { ...listData, newColumn, checkPermissions }
  },
}
</script>
