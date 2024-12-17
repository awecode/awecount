<script>
export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/purchase-order/`
    const listData = useList(endpoint)
    const metaData = {
      title: 'Purchase Orders | Awecount',
    }
    useMeta(metaData)
    const newColumn = [
      {
        name: 'voucher_no',
        label: 'Voucher no',
        align: 'left',
        field: 'voucher_no',
        sortable: true,
      },
      {
        name: 'party_name',
        label: 'Party name',
        align: 'left',
        field: 'party_name',
      },
      { name: 'date', label: 'Date', align: 'left', field: 'date', sortable: true },
      { name: 'status', label: 'Status', align: 'center', field: 'status', sortable: true },
      { name: 'actions' },
    ]

    return { ...listData, newColumn, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div v-if="checkPermissions('ChallanCreate')" class="row q-gutter-x-md justify-end">
      <q-btn color="green" :to="`/${$route.params.company}/purchase-order/create/`" label="New Purchase Order" icon-right="add" class="add-btn" />
    </div>
    <q-table
      v-model:pagination="pagination"
      :rows="rows"
      :columns="newColumn"
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
                    <MultiSelectChip v-model="filters.status" :options="['Issued', 'Cancelled']" />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker
                    v-model:start-date="filters.start_date"
                    v-model:end-date="filters.end_date"
                    :error="true"
                    error-message="asgcvagscvg"
                  />
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="f-submit-btn" @click="onFilterUpdate" />
                  <q-btn color="red" icon="close" class="f-reset-btn" @click="resetFilters" />
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>

      <template #body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center">
            <div
              class="text-white text-subtitle row items-center justify-center"
              :class="props.row.status == 'Issued'
                ? 'bg-blue-2 text-blue-10' : 'bg-red-2 text-red-10'
              "
              style="border-radius: 8px; padding: 2px 10px"
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>

      <template #body-cell-party_name="props">
        <q-td :props="props">
          <div v-if="props.row.party_name">
            <q-icon name="domain" size="sm" class="text-grey-8" />
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">{{ props.row.party_name }}</span>
          </div>
          <div v-else class="row align-center text-subtitle2 text-grey-8">
            {{ props.row.customer_name }}
          </div>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <div class="row q-gutter-x-md">
            <q-btn
              v-if="checkPermissions('PurchaseOrderModify')"
              color="orange"
              label="Edit"
              class="q-py-none q-px-md font-size-sm l-edit-btn"
              style="font-size: 12px"
              :to="`/${$route.params.company}/purchase-order/${props.row.id}/`"
            />
          </div>
        </q-td>
      </template>
      <template #body-cell-voucher_no="props">
        <q-td :props="props">
          <span v-if="props.row.voucher_no">
            <router-link
              v-if="checkPermissions('PurchaseOrderModify')"
              :to="`/${$route.params.company}/purchase-order/${props.row.id}/`"
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
