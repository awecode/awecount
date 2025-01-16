<script>
export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/debit-note/`
    const listData = useList(endpoint)
    const metaData = {
      title: 'Debit Notes | Awecount',
    }
    useMeta(metaData)
    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi(`/api/company/${route.params.company}/debit-note/export${query}`)
        .then(data => usedownloadFile(data, 'application/vnd.ms-excel', 'Debit_Notes'))
        .catch(err => console.log('Error Due To', err))
    }
    const newColumn = [
      {
        name: 'voucher_no',
        label: 'Note No.',
        align: 'left',
        field: 'voucher_no',
        sortable: true,
      },
      {
        name: 'party_name',
        label: 'Party',
        align: 'left',
        field: 'party_name',
      },
      { name: 'status', label: 'Status', align: 'left', field: 'status', sortable: true },
      { name: 'date', label: 'Date', align: 'left', field: 'date', sortable: true },
      { name: 'actions', label: 'Actions', align: 'left' },
    ]

    return { ...listData, onDownloadXls, newColumn, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="flex gap-4 justify-end">
      <q-btn
        class="export-btn"
        color="blue"
        icon-right="download"
        label="Export XLS"
        @click="onDownloadXls"
      />
      <q-btn
        v-if="checkPermissions('debitnote.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New Debit Note"
        :to="`/${$route.params.company}/purchase/debit-notes/create`"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      title="Income Items"
      :columns="newColumn"
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
            class="search-input full-width"
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
                <div class="q-mx-md flex gap-4 q-mb-md q-mt-lg">
                  <q-btn
                    class="f-submit-btn"
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
      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center">
            <div
              class="text-white text-subtitle row items-center justify-center"
              style="border-radius: 8px; padding: 2px 10px"
              :class="
                props.row.status == 'Issued' ? 'bg-blue-2 text-blue-10'
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

      <template #body-cell-party_name="props">
        <q-td :props="props">
          <div>
            <q-icon class="text-grey-8" name="domain" size="sm" />
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{ props.row.party }}</span>
          </div>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <div v-if="checkPermissions('debitnote.view')" class="row q-gutter-x-md items-center">
            <q-btn
              class="q-py-none q-px-md font-size-sm l-view-btn"
              color="blue"
              label="View"
              style="font-size: 12px"
              :to="`/${$route.params.company}/purchase/debit-notes/${props.row.id}`"
            />
          </div>
        </q-td>
      </template>
      <template #body-cell-voucher_no="props">
        <q-td style="padding: 0" :props="props">
          <span v-if="props.row.voucher_no">
            <router-link
              v-if="checkPermissions('debitnote.view')"
              class="text-blue"
              style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
              :to="`/${$route.params.company}/purchase/debit-notes/${props.row.id}`"
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
