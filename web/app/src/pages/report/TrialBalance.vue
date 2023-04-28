<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        color="green"
        label="Export Xls"
        icon-right="download"
        @click="onDownloadXls"
      />
    </div>
    <div class="q-px-md">
      <div class="flex items-center q-gutter-md">
        <div class="q-mx-md">
          <DateRangePicker
            v-model:startDate="fields.start_date"
            v-model:endDate="fields.end_date"
            :hide-btns="true"
          />
        </div>
        <q-btn
          v-if="fields.start_date || fields.end_date"
          color="red"
          icon="close"
          @click="fields = { start_date: null, end_date: null }"
        ></q-btn>
        <q-btn
          :disable="!fields.start_date && !fields.end_date ? true : false"
          color="green"
          label="fetch"
          @click="fetchData"
        ></q-btn>
        <q-btn class="filterbtn" icon="settings" title="Config"></q-btn>
      </div>
    </div>
    <div>
      <q-markup-table>
        <thead>
          <tr>
            <th class="text-left">Name</th>
            <th class="text-left">Opening</th>
            <th class="text-center" colspan="2">Transactions</th>
            <th class="text-left">Closing</th>
          </tr>
          <tr>
            <th class="text-left"></th>
            <th class="text-left">Balance</th>
            <th class="text-left">Dr</th>
            <th class="text-left">Cr</th>
            <th class="text-left">Balance</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="text-left">Frozen Yogurt</td>
            <td class="text-left">159</td>
            <td class="text-left">6</td>
            <td class="text-left">24</td>
            <td class="text-left">4</td>
          </tr>
        </tbody>
      </q-markup-table>
    </div>
  </div>
</template>

<script>
export default {
  setup() {
    const reportData = ref(null)
    const fields = ref({
      start_date: null,
      end_date: null,
    })
    // const endpoint = '/v1/trial-balance/'
    // const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'voucher_no',
      },
      {
        name: 'opening',
        label: 'Opening',
        align: 'left',
        field: 'party_name',
      },
      {
        name: 'transactions',
        label: 'Transactions',
        align: 'center',
        field: 'party_name',
      },
      { name: 'date', label: 'Date', align: 'left', field: 'date' },
    ]
    const fetchData = () => {
      const endpoint = `/v1/trial-balance/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
      useApi(endpoint)
        .then((data) => (reportData.value = data))
        .catch((err) => console.log(err))
      // TODO: add 404 error routing
    }
    // functions
    const onDownloadXls = () => {
      // TODO: add download xls link
      useApi('v1/sales-voucher/export/')
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Credit_Notes'
          )
        )
        .catch((err) => console.log('Error Due To', err))
    }
    return { onDownloadXls, newColumn, fields, fetchData }
  },
}
</script>

<style>
.search-bar {
  display: flex;
  width: 100%;
  column-gap: 20px;
}

.search-bar-wrapper {
  width: 100%;
}

.filterbtn {
  width: 100px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
