<script>
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

export default {
  setup() {
    const metaData = {
      title: 'Sales Discounts | Awecount',
    }
    const route = useRoute()
    useMeta(metaData)
    const endpoint = `/api/company/${route.params.company}/sales-discount/`
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
        sortable: true,
      },
      { name: 'type', label: 'Type', align: 'left', field: 'type', sortable: true },
      {
        name: 'value',
        label: 'Value',
        align: 'left',
        field: 'value',
        sortable: true,
      },
      {
        name: 'trade_discount',
        label: 'Trade Discount',
        align: 'center',
        field: 'trade_discount',
        sortable: true,
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'left',
        field: 'actions',
      },
    ]

    return { ...listData, newColumn, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div v-if="checkPermissions('salesdiscount.delete')" class="row q-gutter-x-md justify-end">
      <q-btn
        class="add-btn"
        color="green"
        icon-right="add"
        label="New sales discount"
        :to="`/${$route.params.company}/sales-discount/create/`"
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
                    <MultiSelectChip v-model="filters.type" :options="['Percent', 'Amount']" />
                  </div>
                  <div class="q-mt-md">
                    <q-checkbox v-model="filters.trade_discount" label="Is Trade Discount?" :false-value="null" />
                  </div>
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

      <template #body-cell-trade_discount="props">
        <q-td :props="props">
          <ShowListBoolean :value="props.row.trade_discount" />
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('salesdiscount.modify')"
            class="q-py-none q-px-md font-size-sm l-edit-btn"
            color="orange-6"
            label="Edit"
            style="font-size: 12px"
            :to="`/${$route.params.company}/sales-discount/${props.row.id}/`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('salesdiscount.modify')"
            class="text-blue"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/sales-discount/${props.row.id}/`"
          >
            {{ props.row.name }}
          </router-link>
          <span
            v-else
            style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
          >
            {{ props.row.name }}
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
