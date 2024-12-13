<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn v-if="checkPermissions('WidgetCreate')" color="green" label="New Dashboard widget" icon-right="add"
        to="/dashboard-widgets/add/" class="add-btn" />
    </div>
    <q-table :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
      row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:body-cell-name="props">
        <q-td :props="props">
          <router-link v-if="checkPermissions('WidgetModify')" :to="`/dashboard-widgets/${props.row.id}/`"
            class="text-blue l-edit-btn" style="text-decoration: none">
            {{ props.row.name }}
          </router-link>
          <span v-else> {{ props.row.name }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  setup() {
    const metaData = {
      title: 'Dashboard Widgets | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/v1/${route.params.company}/widgets/`
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
      },
      {
        name: 'display_type',
        label: 'Display Type',
        align: 'left',
        field: 'display_type',
      },
    ]
    return { ...listData, newColumn, checkPermissions }
  },
}
</script>
