<script>
export default {
  setup() {
    const metaData = {
      title: 'Audit Logs | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/log-entries/`
    const listData = useList(endpoint)
    const onDownloadXls = () => {
      useApi('v1/log-entries/export')
        .then(data => usedownloadFile(data, 'application/vnd.ms-excel', 'Audit Logs'))
        .catch(err => console.log('Error Due To', err))
    }
    const newColumn = [
      {
        name: 'content_type_name',
        label: 'Content Type',
        align: 'left',
        field: 'content_type_name',
      },
      {
        name: 'action',
        label: 'Action',
        align: 'left',
        field: 'action',
      },
      { name: 'user', label: 'User', align: 'left', field: 'actor' },
      {
        name: 'remote_addr',
        label: 'Remote Address',
        align: 'left',
        field: 'remote_addr',
      },
      {
        name: 'datetime',
        label: 'Time',
        align: 'left',
        field: 'datetime',
      },
      { name: 'actions', label: 'Actions', align: 'left' },
    ]

    return { ...listData, newColumn, onDownloadXls }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        class="export-btn"
        color="blue"
        icon-right="download"
        label="Export"
        @click="onDownloadXls"
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
      <template #body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md">
            <q-btn
              class="q-py-none q-px-md font-size-sm"
              color="blue l-view-btn"
              label="Detail"
              style="font-size: 12px"
              :to="`/${$route.params.company}/audit-log/${props.row.id}/`"
            />
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
