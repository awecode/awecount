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
    <q-table
      title="Income Items"
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
      <template v-slot:top>
        <div class="top-bar">
          <!-- <q-input
            dense
            debounce="500"
            v-model="searchQuery"
            placeholder="Search"
            class="search-bar-wrapper"
          >
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input> -->
          <q-btn class="filterbtn" icon="settings" title="Config"></q-btn>
        </div>
      </template>
      <!--
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center">
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
      </template> -->
      <template v-slot:body-cell-party_name="props">
        <q-td :props="props">
          <div v-if="props.row.party_name">
            <q-icon name="domain" size="sm" class="text-grey-8"></q-icon>
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{
              props.row.party_name
            }}</span>
          </div>
          <div v-else class="row align-center text-subtitle2 text-grey-8">
            {{ props.row.customer_name }}
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <!-- {{ props }} -->
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md">
            <q-btn
              color="orange"
              label="Edit"
              :to="`/challan/${props.row.voucher_no}/`"
            />
          </div>
          <!-- {{ props }} -->
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
export default {
  setup() {
    const endpoint = '/v1/trial-balance/'
    const listData = useList(endpoint)
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
    return { ...listData, onDownloadXls, newColumn }
  },
}
// const {
//   columns,
//   rows,
//   resetFilters,
//   filters,
//   loading,
//   searchQuery,
//   pagination,
//   onRequest,
//   confirmDeletion,
//   initiallyLoaded,
// } = useList(endpoint);
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
