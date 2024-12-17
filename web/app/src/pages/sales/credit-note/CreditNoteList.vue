<script>
export default {
  setup() {
    const metaData = {
      title: 'Credit Notes | Awecount',
    }
    useMeta(metaData)
    const newColumns = [
      {
        name: 'voucher_no',
        label: 'Voucher no',
        align: 'left',
        field: 'voucher_no',
        sortable: true,
      },
      { name: 'party', label: 'Party', align: 'left', field: 'party' },
      { name: 'date', label: 'Date', align: 'left', field: 'date', sortable: true },
      { name: 'status', label: 'Status', align: 'left', field: 'status', sortable: true },
      { name: 'actions' },
    ]
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/credit-note/`
    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi(`/api/company/credit-note/export${query}`)
        .then(data =>
          usedownloadFile(
            data,
            'application/vnd.ms-excel',
            'Credit_Notes',
          ),
        )
        .catch(err => console.log('Error Due To', err))
    }
    return { ...useList(endpoint), newColumns, onDownloadXls, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn color="blue" label="Export Xls" icon-right="download" class="export-btn" @click="onDownloadXls" />
      <q-btn
        v-if="checkPermissions('CreditNoteCreate')"
        color="green"
        :to="`/${$route.params.company}/credit-note/add/`"
        label="New Credit Note"
        class="q-ml-lg add-btn"
        icon-right="add"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      :rows="rows"
      :columns="newColumns"
      :loading="loading"
      :filter="searchQuery"
      row-key="id"
      class="q-mt-md"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <div class="search-bar">
          <q-input v-model="searchQuery" dense debounce="500" placeholder="Search" class="full-width search-input">
            <template #append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="f-open-btn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(550px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">
                    Filters
                  </h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-ma-sm">
                    <MultiSelectChip v-model="filters.status" :options="['Draft', 'Issued', 'Cancelled', 'Resolved']" />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:start-date="filters.start_date" v-model:end-date="filters.end_date" />
                </div>
                <div class="q-mx-md row q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="q-mr-md f-submit-btn" @click="onFilterUpdate" />
                  <q-btn color="red" icon="close" class="f-reset-btn" @click="resetFilters" />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props" class="row justify center">
          <q-btn
            v-if="checkPermissions('CreditNoteView')"
            color="blue"
            class="q-py-none q-px-md font-size-sm l-view-btn"
            style="font-size: 12px"
            label="View"
            :to="`/${$route.params.company}/credit-note/${props.row.id}/view`"
          />
        </q-td>
      </template>
      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center">
            <div
              class="text-white text-subtitle row items-center justify-center"
              :class="props.row.status == 'Issued'
                ? 'bg-blue-2 text-blue-9'
                : props.row.status == 'Resolved'
                  ? 'bg-green-2 text-green-10'
                  : props.row.status == 'Draft' ? 'bg-orange-2 text-orange-10' : 'bg-red-2 text-red-10'
              "
              style="border-radius: 8px; padding: 2px 10px"
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
      <template #body-cell-party="props">
        <q-td :props="props">
          <div>
            <q-icon name="domain" size="sm" class="text-grey-8" />
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{
              props.row.party
            }}</span>
          </div>
        </q-td>
      </template>
      <template #body-cell-voucher_no="props">
        <q-td :props="props">
          <span v-if="props.row.voucher_no">
            <router-link
              v-if="checkPermissions('CreditNoteView')"
              :to="`/${$route.params.company}/credit-note/${props.row.id}/view`"
              style="font-weight: 500; text-decoration: none"
              class="text-blue"
            >
              {{ props.row.voucher_no }}
            </router-link>
            <span v-else>
              {{ props.row.voucher_no }}
            </span>
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
