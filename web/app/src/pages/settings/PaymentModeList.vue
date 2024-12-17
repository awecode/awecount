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
        v-if="checkPermissions('PaymentModeCreate')"
        color="green"
        to="/settings/payment-mode/add/"
        label="New Payment Mode"
        icon-right="add"
        class="add-btn"
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
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md">
            <q-btn
              class="q-py-none q-px-md font-size-sm"
              style="font-size: 12px"
              color="blue l-view-btn"
              label="Edit"
              :to="`/settings/payment-mode/${props.row.id}/`"
            />
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
