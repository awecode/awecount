<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn v-if="checkPermissions('SalesAgentCreate')" color="green" to="/sales-agent/add/" label="Sales Agent" icon-right="add" class="add-btn" />
    </div>
    <q-table :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link v-if="checkPermissions('SalesAgentModify')" class="text-blue l-edit-btn whitespace-normal" style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px" :to="`/sales-agent/${props.row.id}/`">
            {{ props.row.name }}
          </router-link>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">{{ props.row.name }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
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

    return { ...listData, newColumn, checkPermissions }
  },
}
</script>
