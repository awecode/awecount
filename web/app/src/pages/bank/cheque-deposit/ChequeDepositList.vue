<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn
        color="green"
        to="/bank/cheque/cheque-deposit/add/"
        label="New Cheque Deposit"
        class="q-ml-lg"
        icon-right="add"
      />
    </div>

    <q-table
      title="Cheque Deposits"
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
                  <div class="q-mx-sm">
                    <SelectWithFetch
                      v-model="filters.bank_account"
                      endpoint="v1/bank-account/choices/"
                      label="Bank Account"
                    />
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip
                      v-model="filters.status"
                      :options="['Issued', 'Cancelled']"
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
                  : props.row.status == 'Cleared'
                  ? 'bg-green'
                  : 'bg-red'
              "
              style="border-radius: 30px; padding: 5px 15px"
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            label="View"
            color="blue"
            class="q-py-none q-px-md font-size-sm"
            style="font-size: 12px"
            :to="`/bank/cheque/cheque-deposit/${props.row.id}/view/`"
          />
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
export default {
  setup() {
    const metaData = {
      title: 'Cheque Deposits | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/cheque-deposits/'
    const newColumn = [
      {
        name: 'bank_account',
        label: 'Bank Account',
        align: 'left',
        field: 'bank_account',
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
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    return { ...useList(endpoint), newColumn }
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
  width: 80px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
