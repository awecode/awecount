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
      <template v-slot:body-cell-name="props">
        <q-td :props="props">
          <router-link
            class="text-blue"
            style="text-decoration: none"
            :to="`/sales-agent/${props.row.id}/`"
          >
            {{ props.row.name }}
          </router-link>
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
      title: 'Sales Agents | Awecount',
    }
    useMeta(metaData)
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
