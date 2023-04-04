<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        color="blue"
        label="Export XLS"
        icon-right="download"
        @click="onDownloadXls"
      />
      <q-btn
        color="green"
        to="/purchase-voucher/add/"
        label="New Purchase"
        icon-right="add"
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
                  <div class="q-mb-sm">
                    <q-checkbox
                      v-model="filters.is_due"
                      label="Is Due?"
                      :false-value="null"
                    ></q-checkbox>
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip
                      :options="[
                        'Draft',
                        'Issued',
                        'Paid',
                        'Partially Paid',
                        'Cancelled',
                      ]"
                      v-model="filters.status"
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

      <template v-slot:body-cell-party_name="props">
        <q-td :props="props">
          <div>
            <q-icon name="domain" size="sm" class="text-grey-8"></q-icon>
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{
              props.row.party
            }}</span>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md items-center">
            <q-btn
              color="blue"
              label="View"
              :to="`/purchase-voucher/${props.row.id}/view`"
              class="q-py-none q-px-md font-size-sm"
              style="font-size: 12px"
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
    const metaData = {
      title: 'Purchases/Expenses | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/purchase-vouchers/'
    const listData = useList(endpoint)
    const route = useRoute()
    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi('v1/purchase-vouchers/export' + query)
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Purchase_voucher'
          )
        )
        .catch((err) => console.log('Error Due To', err))
    }
    const newColumn = [
      {
        name: 'voucher_no',
        label: 'Bill No.',
        align: 'left',
        field: 'voucher_no',
      },
      {
        name: 'party_name',
        label: 'Party',
        align: 'left',
        field: 'party_name',
      },
      { name: 'status', label: 'Status', align: 'center', field: 'status' },
      { name: 'date', label: 'Date', align: 'left', field: 'date' },
      {
        name: 'mode',
        label: 'Mode',
        align: 'left',
        field: 'mode',
      },
      {
        name: 'total_amount',
        label: 'Total amount',
        align: 'left',
        field: 'total_amount',
      },
      { name: 'actions', label: 'Actions', align: 'left' },
    ]

    return { ...listData, onDownloadXls, newColumn }
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
