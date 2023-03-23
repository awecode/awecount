<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        color="blue"
        label="Export"
        icon-right="download"
        @click="onDownloadXls"
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
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md">
            <q-btn
              class="q-py-none q-px-md font-size-sm"
              style="font-size: 12px"
              color="blue"
              label="Detail"
              :to="`/audit-log/${props.row.id}/`"
            />
          </div>
        </q-td>
        <!-- TODO: add modals -->
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
import usedownloadFile from 'src/composables/usedownloadFile'
export default {
  setup() {
    const endpoint = '/v1/log-entries/'
    const listData = useList(endpoint)
    const onDownloadXls = () => {
      useApi('v1/log-entries/export/')
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Audit Logs'
          )
        )
        .catch((err) => console.log('Error Due To', err))
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
