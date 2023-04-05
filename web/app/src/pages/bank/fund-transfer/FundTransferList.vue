<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn
        color="green"
        to="/fund-transfer/add/"
        label="New Fund Transfer"
        class="q-ml-lg"
        icon-right="add"
      />
    </div>

    <q-table
      title="Fund Transfer"
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
            label="Edit"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm"
            style="font-size: 12px"
            :to="`/fund-transfer/${props.row.id}/`"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-voucher_no="props">
        <q-td :props="props">
          <router-link
            class="text-blue text-weight-medium"
            style="text-decoration: none"
            :to="`/fund-transfer/${props.row.id}/`"
            >{{ props.row.voucher_no }}</router-link
          >
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
export default {
  setup() {
    const endpoint = '/v1/fund-transfer/'
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
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
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
      },
      {
        name: 'status',
        label: 'Status',
        align: 'center',
        field: 'status',
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
