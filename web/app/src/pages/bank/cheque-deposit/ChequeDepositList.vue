<script>
export default {
  setup() {
    const metaData = {
      title: 'Cheque Deposits | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/cheque-deposits/`
    const newColumn = [
      {
        name: 'bank_account_name',
        label: 'Bank Account',
        align: 'left',
        field: 'bank_account_name',
      },
      {
        name: 'benefactor_name',
        label: 'Benefactor',
        align: 'left',
        field: 'benefactor_name',
      },
      {
        name: 'status',
        label: 'Status',
        align: 'center',
        field: 'status',
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
        v-if="checkPermissions('chequedeposit.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New Cheque Deposit"
        :to="`/${$route.params.company}/cheque-deposit/create/`"
      />
    </div>

    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      title="Cheque Deposits"
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
                  <div class="q-mx-sm">
                    <n-auto-complete-v2
                      v-model="filters.bank_account"
                      label="Bank Account"
                      :endpoint="`/api/company/${$route.params.company}/bank-account/choices/`"
                      :fetch-on-mount="true"
                    />
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip v-model="filters.status" :options="['Issued', 'Draft', 'Cleared', 'Cancelled']" />
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
          <div class="row align-center justify-center">
            <div
              class="text-white text-subtitle row items-center justify-center"
              style="border-radius: 8px; padding: 2px 10px"
              :class="
                props.row.status == 'Issued' ? 'bg-blue-2 text-blue-10'
                : props.row.status == 'Draft' ? 'bg-orange-2 text-orange-10'
                  : props.row.status == 'Cleared' ? 'bg-green-2 text-green-10'
                    : 'bg-red-2 text-red-10'
              "
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            class="q-py-none q-px-md font-size-sm l-view-btn"
            color="blue"
            label="View"
            style="font-size: 12px"
            :to="`/${$route.params.company}/cheque-deposit/${props.row.id}/view/`"
          />
        </q-td>
      </template>
    </q-table>
  </div>
</template>
