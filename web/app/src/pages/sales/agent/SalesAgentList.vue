<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        color="green"
        to="/sales-agent/add/"
        label="Sales Agent"
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
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
export default {
  setup() {
    const endpoint = '/v1/sales-agent/'
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
      },
      {
        name: 'compensation_multiplier',
        label: 'Compensation Multiplier',
        align: 'left',
        field: 'compensation_multiplier',
      },
    ]

    return { ...listData, newColumn }
  },
}
</script>
