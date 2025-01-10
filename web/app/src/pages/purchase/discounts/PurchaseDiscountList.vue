<script>
export default {
  setup() {
    const metaData = {
      title: 'Purchase Discounts | Awecount',
    }
    const route = useRoute()
    useMeta(metaData)
    const endpoint = `/api/company/${route.params.company}/purchase-discount/`
    const listData = useList(endpoint)
    const onDownloadXls = () => {
      useApi(`/api/company/${route.params.company}/sales-voucher/export`)
        .then(data =>
          usedownloadFile(
            data,
            'application/vnd.ms-excel',
            'Credit_Notes',
          ),
        )
        .catch(err => console.log('Error Due To', err))
    }
    const newColumn = [
      {
        name: 'voucher_no',
        label: 'Name.',
        align: 'left',
        field: 'name',
        sortable: true,
      },
      { name: 'type', label: 'Type', align: 'left', field: 'type', sortable: true },
      { name: 'value', label: 'Value', align: 'left', field: 'value', sortable: true },
      {
        name: 'trade_discount',
        label: 'Trade Discount',
        align: 'center',
        field: 'trade_discount',
        sortable: true,
      },
      { name: 'actions', label: 'Actions', align: 'left' },
    ]

    return { ...listData, onDownloadXls, newColumn, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        v-if="checkPermissions('purchasediscount.create')"
        color="green"
        :to="`/${$route.params.company}/purchase-discount/create/`"
        label="New Purchase Discount"
        icon-right="add"
        class="add-btn"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      title="Income Items"
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
                    <q-checkbox
                      v-model="filters.trade_discount"
                      label="Is Trade Discount?"
                      :false-value="null"
                    />
                  </div>
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
      <template #body-cell-actions="props">
        <q-td :props="props">
          <div class="row q-gutter-x-md items-center">
            <q-btn
              v-if="checkPermissions('purchasediscount.modify')"
              color="orange-7"
              label="Edit"
              :to="`/${$route.params.company}/purchase-discount/${props.row.id}/`"
              class="q-py-none q-px-md font-size-sm l-edit-btn"
              style="font-size: 12px"
            />
          </div>
        </q-td>
      </template>
      <template #body-cell-trade_discount="props">
        <q-td :props="props">
          <div class="row justify-center">
            <ShowListBoolean :value="props.row.trade_discount" />
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
