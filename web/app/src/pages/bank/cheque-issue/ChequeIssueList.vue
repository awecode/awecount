<template>
  <div class="q-pa-md">
    <div class="row q-guuter-x-sm justify-end">
      <q-btn
        color="blue"
        label="Export"
        icon-right="download"
        @click="onDownloadXls"
      />
      <q-btn
        color="green"
        to="/bank/cheque/cheque-issue/add/"
        label="New Cheque Issue"
        class="q-ml-lg"
        icon-right="add"
      />
    </div>

    <q-table
      title="Cheque Issues"
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
      <template v-slot:top-right>
        <q-input
          borderless
          dense
          debounce="500"
          v-model="searchQuery"
          placeholder="Search"
        >
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body-cell-issued_to="props">
        <q-td :props="props">
          <router-link
            style="font-weight: 500; text-decoration: none"
            class="text-blue"
            :to="`/bank/cheque/cheque-issue/${props.row.id}/edit/`"
            >{{ props.row.issued_to }}</router-link
          >
        </q-td>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center">
            <div
              class="text-white text-subtitle2 row items-center justify-center"
              :class="
                props.row.status == 'Issued'
                  ? 'bg-blue'
                  : props.row.status == 'Paid'
                  ? 'bg-green'
                  : props.row.status == 'Draft'
                  ? 'bg-orange'
                  : 'bg-red'
              "
              style="border-radius: 30px; padding: 5px 15px"
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            label="Edit"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm"
            style="font-size: 12px"
            :to="`/bank/cheque/cheque-issue/${props.row.id}/edit/`"
          />
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
export default {
  setup() {
    const endpoint = '/v1/cheque-issue/'
    const newColumn = [
      {
        name: 'issued_to',
        label: 'TO',
        align: 'left',
        field: 'issued_to',
      },
      {
        name: 'cheque_no',
        label: 'Cheque #',
        align: 'left',
        field: 'cheque_no',
      },
      {
        name: 'amount',
        label: 'Amount',
        align: 'left',
        field: 'amount',
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
      },
      {
        name: 'status',
        label: 'Status',
        align: 'center',
        field: 'status',
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    const onDownloadXls = () => {
      useApi('v1/cheque-issued/export/')
        // TODO: url not found
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Cheque Issued'
          )
        )
        .catch((err) => console.log('Error Due To', err))
    }
    return { ...useList(endpoint), newColumn, onDownloadXls }
  },
}
</script>
