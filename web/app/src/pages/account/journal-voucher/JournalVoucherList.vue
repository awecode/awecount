<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn v-if="checkPermissions('JournalVoucherCreate')" color="green" to="/journal-voucher/add/"
        label="New Journal Voucher" class="add-btn" icon-right="add" />
    </div>

    <q-table :rows="rows" :columns="newColumns" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
      row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <div class="search-bar">
          <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="full-width search-input">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="f-open-btn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(500px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-ma-sm">
                    <MultiSelectChip :options="['Cancelled', 'Approved', 'Unapproved']" v-model="filters.status" />
                  </div>
                  <div class="q-mx-md">
                    <DateRangePicker v-model:startDate="filters.start_date" v-model:endDate="filters.end_date" />
                  </div>
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md">
                  <q-btn color="green" label="Filter" @click="onFilterUpdate" class="f-submit-btn"></q-btn>
                  <q-btn color="red" icon="close" @click="resetFilters" class="f-reset-btn"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <div class="flex gap-4 no-wrap">
            <q-btn v-if="checkPermissions('JournalVoucherView')" color="blue" label="View" :to="`/journal-voucher/${props.row.id}/view/`"
              class="q-py-none q-px-md font-size-sm l-view-btn" style="font-size: 12px" />
            <q-btn v-if="props.row.status !== 'Cancelled' && checkPermissions('JournalVoucherModify')" color="orange-7"
              label="Edit" :to="`/journal-voucher/${props.row.id}/edit/`" class="q-py-none q-px-md font-size-sm l-edit-btn"
              style="font-size: 12px" />
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <div class="row q-gutter-sm justify-center">
            <span class="text-white text-subtitle" :class="props.row.status === 'Unapproved'
              ? 'bg-orange-2 text-orange-10'
              : props.row.status === 'Approved'
                ? 'bg-green-2 text-green-10'
                : 'bg-red-2 text-red-10'
              " style="border-radius: 8px; padding: 2px 10px">{{ props.row.status }}</span>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-voucher_no="props">
        <q-td :props="props">
          <span v-if="props.row.voucher_no">
            <router-link v-if="checkPermissions('JournalVoucherView')" :to="`/challan/${props.row.id}/`"
              style="font-weight: 500; text-decoration: none" class="text-blue">
              {{ props.row.voucher_no }}
            </router-link>
            <span v-else>{{ props.row.voucher_no }}</span>
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
export default {
  setup() {
    const metaData = {
      title: 'Journal Vouchers | Awecount',
    }
    const route = useRoute()
    useMeta(metaData)
    const endpoint = `/v1/${route.params.company}/journal-voucher/`
    const newColumns = [
      {
        name: 'voucher_no',
        label: 'Voucher No.',
        align: 'left',
        field: 'voucher_no',
        sortable: true
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
        sortable: true
      },
      { name: 'status', label: 'Status', align: 'center', field: 'status', sortable: true},
      {
        name: 'narration',
        label: 'Narration',
        align: 'left',
        field: 'narration',
      },
      { name: 'actions', label: 'Actions', align: 'center' },
    ]
    return { ...useList(endpoint), newColumns, checkPermissions }
  },
}
</script>
