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
    const endpoint = '/v1/credit-note/'
    const route = useRoute()
    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi(`/v1/credit-note/export${query}`)
        .then(data => usedownloadFile(data, 'application/vnd.ms-excel', 'Credit_Notes'))
        .catch(err => console.log('Error Due To', err))
    }
    return { ...useList(endpoint), newColumns, onDownloadXls, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn
        class="export-btn"
        color="blue"
        icon-right="download"
        label="Export Xls"
        @click="onDownloadXls"
      />
      <q-btn
        v-if="checkPermissions('CreditNoteCreate')"
        class="q-ml-lg add-btn"
        color="green"
        icon-right="add"
        label="New Credit Note"
        to="/credit-note/add/"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      :columns="newColumns"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <div class="search-bar">
          <q-input
            v-model="searchQuery"
            dense
            class="full-width search-input"
            debounce="500"
            placeholder="Search"
          >
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
                  <DateRangePicker v-model:end-date="filters.end_date" v-model:start-date="filters.start_date" />
                </div>
                <div class="q-mx-md row q-mb-md q-mt-lg">
                  <q-btn
                    class="q-mr-md f-submit-btn"
                    color="green"
                    label="Filter"
                    @click="onFilterUpdate"
                  />
                  <q-btn
                    class="f-reset-btn"
                    color="red"
                    icon="close"
                    @click="resetFilters"
                  />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template #body-cell-actions="props">
        <q-td class="row justify center" :props="props">
          <q-btn
            v-if="checkPermissions('CreditNoteView')"
            class="q-py-none q-px-md font-size-sm l-view-btn"
            color="blue"
            label="View"
            style="font-size: 12px"
            :to="`/credit-note/${props.row.id}/view`"
          />
        </q-td>
      </template>
      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center">
            <div
              class="text-white text-subtitle row items-center justify-center"
              style="border-radius: 8px; padding: 2px 10px"
              :class="
                props.row.status == 'Issued' ? 'bg-blue-2 text-blue-9'
                : props.row.status == 'Resolved' ? 'bg-green-2 text-green-10'
                  : props.row.status == 'Draft' ? 'bg-orange-2 text-orange-10'
                    : 'bg-red-2 text-red-10'
              "
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
      <template #body-cell-party="props">
        <q-td :props="props">
          <div>
            <q-icon class="text-grey-8" name="domain" size="sm" />
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{ props.row.party }}</span>
          </div>
        </q-td>
      </template>
      <template #body-cell-voucher_no="props">
        <q-td style="padding: 0" :props="props">
          <span v-if="props.row.voucher_no">
            <router-link
              v-if="checkPermissions('CreditNoteView')"
              class="text-blue"
              style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
              :to="`/credit-note/${props.row.id}/view`"
            >
              {{ props.row.voucher_no }}
            </router-link>
            <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
              {{ props.row.voucher_no }}
            </span>
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
