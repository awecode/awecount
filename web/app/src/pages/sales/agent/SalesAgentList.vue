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
        v-if="checkPermissions('salesagent.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="Sales Agent"
        :to="`/${$route.params.company}/sales-agent/create/`"
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
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('salesagent.modify')"
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
