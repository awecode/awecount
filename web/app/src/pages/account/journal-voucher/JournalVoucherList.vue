<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn
        color="green"
        to="/journal-voucher/add/"
        label="New Journal Voucher"
        class="q-ml-lg"
        icon-right="add"
      />
    </div>

    <q-table
      :rows="rows"
      :columns="newColumns"
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
              <div class="menu-wrapper" style="width: min(500px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-ma-sm">
                    <MultiSelectChip
                      :options="['Cancelled', 'Approved', 'Unapproved']"
                      v-model="filters.status"
                    />
                  </div>
                  <div class="q-mx-md">
                    <DateRangePicker
                      v-model:startDate="filters.start_date"
                      v-model:endDate="filters.end_date"
                    />
                  </div>
                </div>
                <div class="q-mx-md row q-gutter-md q-mb-md">
                  <q-btn
                    color="green"
                    label="Filter"
                    @click="onFilterUpdate"
                  ></q-btn>
                  <q-btn color="red" icon="close" @click="resetFilters"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <div class="row q-gutter-sm justify-center">
            <q-btn
              color="blue"
              label="View"
              :to="`/journal-voucher/${props.row.id}/view/`"
              class="q-py-none q-px-md font-size-sm"
              style="font-size: 12px"
            />
            <q-btn
              v-if="props.row.status != 'Cancelled'"
              color="orange-7"
              label="Edit"
              :to="`/journal-voucher/${props.row.id}/edit/`"
              class="q-py-none q-px-md font-size-sm"
              style="font-size: 12px"
            />
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <div class="row q-gutter-sm justify-center">
            <span
              class="text-white text-weight-medium"
              :class="
                props.row.status === 'Unapproved'
                  ? 'bg-orange-4'
                  : props.row.status === 'Approved'
                  ? 'bg-green-4'
                  : 'bg-red-4'
              "
              style="border-radius: 2rem; padding: 5px 10px"
              >{{ props.row.status }}</span
            >
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
export default {
  setup() {
    const endpoint = '/v1/journal-voucher/'
    const newColumns = [
      {
        name: 'voucher_no',
        label: 'Voucher No.',
        align: 'left',
        field: 'voucher_no',
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
      },
      { name: 'status', label: 'Status', align: 'center', field: 'status' },
      {
        name: 'narration',
        label: 'Narration',
        align: 'left',
        field: 'narration',
      },
      { name: 'actions', label: 'Actions', align: 'center' },
    ]
    return { ...useList(endpoint), newColumns }
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
