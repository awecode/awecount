<script>
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

export default {
  setup() {
    const metaData = {
      title: 'Dashboard Widgets | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/widgets/`
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

<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        v-if="checkPermissions('WidgetCreate')"
        color="green"
        label="New Dashboard widget"
        icon-right="add"
        :to="`/${$route.params.company}/dashboard-widgets/create/`"
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
            v-if="checkPermissions('WidgetModify')"
            :to="`/${$route.params.company}/dashboard-widgets/${props.row.id}/`"
            class="text-blue l-edit-btn"
            style="text-decoration: none"
          >
            {{ props.row.name }}
          </router-link>
          <span v-else> {{ props.row.name }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
