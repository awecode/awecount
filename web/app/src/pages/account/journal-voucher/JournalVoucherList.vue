<script>
export default {
  setup() {
    const metaData = {
      title: 'Journal Vouchers | Awecount',
    }
    const route = useRoute()
    useMeta(metaData)
    const endpoint = `/api/company/${route.params.company}/journal-voucher/`
    const newColumns = [
      {
        name: 'voucher_no',
        label: 'Voucher No.',
        align: 'left',
        field: 'voucher_no',
        sortable: true,
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
        sortable: true,
      },
      { name: 'status', label: 'Status', align: 'center', field: 'status', sortable: true },
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

<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn
        v-if="checkPermissions('JournalVoucherCreate')"
        color="green"
        :to="`/${$route.params.company}/journal-voucher/create/`"
        label="New Journal Voucher"
        class="add-btn"
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
              <div class="menu-wrapper" style="width: min(500px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">
                    Filters
                  </h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-ma-sm">
                    <MultiSelectChip v-model="filters.status" :options="['Cancelled', 'Approved', 'Unapproved']" />
                  </div>
                  <div class="q-mx-md">
                    <DateRangePicker v-model:start-date="filters.start_date" v-model:end-date="filters.end_date" />
                  </div>
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md">
                  <q-btn color="green" label="Filter" class="f-submit-btn" @click="onFilterUpdate" />
                  <q-btn color="red" icon="close" class="f-reset-btn" @click="resetFilters" />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <div class="flex gap-4 no-wrap">
            <q-btn
              v-if="checkPermissions('JournalVoucherView')"
              color="blue"
              label="View"
              :to="`/${$route.params.company}/journal-voucher/${props.row.id}/view/`"
              class="q-py-none q-px-md font-size-sm l-view-btn"
              style="font-size: 12px"
            />
            <q-btn
              v-if="props.row.status !== 'Cancelled' && checkPermissions('JournalVoucherModify')"
              color="orange-7"
              label="Edit"
              :to="`/${$route.params.company}/journal-voucher/${props.row.id}/edit/`"
              class="q-py-none q-px-md font-size-sm l-edit-btn"
              style="font-size: 12px"
            />
          </div>
        </q-td>
      </template>
      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row q-gutter-sm justify-center">
            <span
              class="text-white text-subtitle"
              :class="props.row.status === 'Unapproved'
                ? 'bg-orange-2 text-orange-10'
                : props.row.status === 'Approved'
                  ? 'bg-green-2 text-green-10'
                  : 'bg-red-2 text-red-10'
              "
              style="border-radius: 8px; padding: 2px 10px"
            >{{ props.row.status }}</span>
          </div>
        </q-td>
      </template>
      <template #body-cell-voucher_no="props">
        <q-td :props="props">
          <span v-if="props.row.voucher_no">
            <router-link
              v-if="checkPermissions('JournalVoucherView')"
              :to="`/${$route.params.company}/challan/${props.row.id}/`"
              style="font-weight: 500; text-decoration: none"
              class="text-blue"
            >
              {{ props.row.voucher_no }}
            </router-link>
            <span v-else>{{ props.row.voucher_no }}</span>
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
