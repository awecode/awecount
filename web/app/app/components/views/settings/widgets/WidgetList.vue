<script>
import checkPermissions from '@/composables/checkPermissions'
import useList from '@/composables/useList'

export default defineNuxtComponent({
  setup() {
    const metaData = {
      title: 'Dashboard Widgets | Awecount',
    }
    useHead(metaData)
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
})
</script>

<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        v-if="checkPermissions('widget.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New Dashboard widget"
        :to="`/${$route.params.company}/settings/dashboard-widgets/create`"
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
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('widget.update')"
            class="text-blue l-edit-btn"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/settings/dashboard-widgets/${props.row.id}/edit`"
          >
            {{ props.row.name }}
          </router-link>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
            {{ props.row.name }}
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
