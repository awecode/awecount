<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        color="green"
        label="New Dashboard widget"
        icon-right="add"
        to="/dashboard-widgets/add/"
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
            :to="`/dashboard-widgets/${props.row.id}/`"
            class="text-blue"
            style="text-decoration: none"
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
    const endpoint = '/v1/widgets/'
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
    return { ...listData, newColumn }
  },
}
</script>
