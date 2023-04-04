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
        <div class="search-bar">
          <q-input
            dense
            debounce="500"
            v-model="searchQuery"
            placeholder="Search"
            class="search-bar-wrapper"
          >
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="filterbtn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(550px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mx-sm">
                    <SelectWithFetch
                      v-model="filters.bank_account"
                      endpoint="v1/bank-account/choices/"
                      label="Bank Account"
                    />
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip
                      v-model="filters.status"
                      :options="['Draft', 'Issued', 'Cleared']"
                    />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker
                    v-model:startDate="filters.start_date"
                    v-model:endDate="filters.end_date"
                  />
                </div>
                <div class="q-mx-md row q-mb-md q-mt-lg">
                  <q-btn
                    color="green"
                    label="Filter"
                    class="q-mr-md"
                    @click="onFilterUpdate"
                  ></q-btn>
                  <q-btn color="red" icon="close" @click="resetFilters"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
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
                  : props.row.status == 'Cleared'
                  ? 'bg-green'
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
    const metaData = {
      title: 'Cheque Issues | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/cheque-issue/'
    const route = useRoute()
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
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi('v1/cheque-issued/export/' + query)
        //   // TODO: url not found
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Sales_voucher'
          )
        )
        .catch((err) => console.log('Error Due To', err))
    }
    return { ...useList(endpoint), newColumn, onDownloadXls }
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
  width: 80px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
