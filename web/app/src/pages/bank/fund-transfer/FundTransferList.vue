<script>
export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/fund-transfer/`
    const metaData = {
      title: 'Fund Transfers | Awecount',
    }
    useMeta(metaData)
    const newColumn = [
      {
        name: 'voucher_no',
        label: 'Voucher #',
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
      {
        name: 'from',
        label: 'From',
        align: 'left',
        field: 'from_account_name',
      },
      {
        name: 'to',
        label: 'To',
        align: 'left',
        field: 'to_account_name',
      },
      {
        name: 'amount',
        label: 'Amount',
        align: 'center',
        field: 'amount',
        sortable: true,
      },
      {
        name: 'status',
        label: 'Status',
        align: 'center',
        field: 'status',
        sortable: true,
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    return { ...useList(endpoint), newColumn, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn
        v-if="checkPermissions('FundTransferCreate')"
        color="green"
        :to="`/${$route.params.company}/fund-transfer/create/`"
        label="New Fund Transfer"
        class="add-btn"
        icon-right="add"
      />
    </div>
    <q-card v-if="data?.templates && data.templates.length" class="p-4 mt-4">
      <h5 class="q-my-none q-mb-sm text-h6 text-grey-8">
        Templates:
      </h5>
      <div class="flex gap-4">
        <q-btn
          v-for="template in data.templates"
          :key="template.id"
          class="add-btn"
          icon-right="add"
          color="green"
          :label="template.name"
          :to="{ path: `/${$route.params.company}/fund-transfer/create/`, query: { template: encodeURIComponent(JSON.stringify(template)) } }"
        />
      </div>
    </q-card>
    <q-table
      v-model:pagination="pagination"
      title="Fund Transfer"
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
                  <DateRangePicker v-model:start-date="filters.start_date" v-model:end-date="filters.end_date" />
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
                ? 'bg-blue-2 text-blue-10'
                : props.row.status == 'Cleared'
                  ? 'bg-green-2 text-green-10'
                  : 'bg-red-2 text-red-10'
              "
              style="border-radius: 8px; padding: 2px 10px"
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('FundTransferModify')"
            label="Edit"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm l-edit-btn"
            style="font-size: 12px"
            :to="`/${$route.params.company}/fund-transfer/${props.row.id}/`"
          />
        </q-td>
      </template>
      <template #body-cell-voucher_no="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('FundTransferModify')"
            class="text-blue text-weight-medium"
            style="text-decoration: none"
            :to="`/${$route.params.company}/fund-transfer/${props.row.id}/`"
          >
            {{ props.row.voucher_no }}
          </router-link>
          <span v-else> {{ props.row.voucher_no }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
