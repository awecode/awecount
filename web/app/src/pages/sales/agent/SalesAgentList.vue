<script>
export default {
  setup() {
    const metaData = {
      title: 'Sales Agents | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/sales-agent/`
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

<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        v-if="checkPermissions('SalesAgentCreate')"
        color="green"
        :to="`/${$route.params.company}/sales-agent/create/`"
        label="Sales Agent"
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
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('SalesAgentModify')"
            class="text-blue l-edit-btn whitespace-normal"
            style="text-decoration: none"
            :to="`/${$route.params.company}/sales-agent/${props.row.id}/`"
          >
            {{ props.row.name }}
          </router-link>
          <span v-else class="whitespace-normal">{{ props.row.name }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
