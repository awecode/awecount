<script>
export default {
  setup() {
    const metaData = {
      title: 'Payment Modes | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/payment-modes/`
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

<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        v-if="checkPermissions('paymentmode.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New Payment Mode"
        :to="`/${$route.params.company}/settings/payment-modes/create`"
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
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md">
            <q-btn
              class="q-py-none q-px-md font-size-sm"
              color="blue l-view-btn"
              label="Edit"
              style="font-size: 12px"
              :to="`/${$route.params.company}/settings/payment-modes/${props.row.id}/edit/`"
            />
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
