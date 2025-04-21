<script>
export default {
  setup() {
    const metaData = {
      title: 'Journal Vouchers | Awecount',
    }
    const route = useRoute()
    useHead(metaData)
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
        v-if="checkPermissions('journalvoucher.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New Journal Voucher"
        :to="`/${$route.params.company}/account/journal-vouchers/create`"
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
                    <DateRangePicker v-model:end-date="filters.end_date" v-model:start-date="filters.start_date" />
                  </div>
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md">
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
      <template #body-cell-actions="props">
        <q-td :props="props">
          <div class="flex gap-4 no-wrap">
            <q-btn
              v-if="checkPermissions('journalvoucher.read')"
              class="q-py-none q-px-md font-size-sm l-view-btn"
              color="blue"
              label="View"
              style="font-size: 12px"
              :to="`/${$route.params.company}/account/journal-vouchers/${props.row.id}`"
            />
            <q-btn
              v-if="props.row.status !== 'Cancelled' && checkPermissions('journalvoucher.update')"
              class="q-py-none q-px-md font-size-sm l-edit-btn"
              color="orange-7"
              label="Edit"
              style="font-size: 12px"
              :to="`/${$route.params.company}/account/journal-vouchers/${props.row.id}/edit`"
            />
          </div>
        </q-td>
      </template>
      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row q-gutter-sm justify-center">
            <span
              class="text-white text-subtitle"
              style="border-radius: 8px; padding: 2px 10px"
              :class="
                props.row.status === 'Unapproved' ? 'bg-orange-2 text-orange-10'
                : props.row.status === 'Approved' ? 'bg-green-2 text-green-10'
                  : 'bg-red-2 text-red-10'
              "
            >
              {{ props.row.status }}
            </span>
          </div>
        </q-td>
      </template>
      <template #body-cell-voucher_no="props">
        <q-td style="padding: 0" :props="props">
          <span v-if="props.row.voucher_no">
            <router-link
              v-if="checkPermissions('journalvoucher.read')"
              class="text-blue"
              style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
              :to="`/${$route.params.company}/account/journal-vouchers/${props.row.id}`"
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
