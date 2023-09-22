<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn v-if="checkPermissions('PurchaseDiscountCreate')" color="green" to="/purchase-discount/add/"
        label="New Purchase Discount" icon-right="add" />
    </div>
    <q-table title="Income Items" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery"
      v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <div class="search-bar">
          <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="search-bar-wrapper">
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
                    <MultiSelectChip v-model="filters.type" :options="['Percent', 'Amount']" />
                  </div>
                  <div class="q-mt-md">
                    <q-checkbox v-model="filters.trade_discount" label="Is Trade Discount?"
                      :false-value="null"></q-checkbox>
                  </div>
                </div>
                <div class="q-mx-md row q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="q-mr-md" @click="onFilterUpdate"></q-btn>
                  <q-btn color="red" icon="close" @click="resetFilters"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row q-gutter-x-md items-center">
            <q-btn v-if="checkPermissions('PurchaseDiscountModify')" color="orange-7" label="Edit"
              :to="`/purchase-discount/${props.row.id}/`" class="q-py-none q-px-md font-size-sm"
              style="font-size: 12px" />
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-trade_discount="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="grey" dense flat to="" /> -->
          <div class="row justify-center">
            <q-checkbox v-model="props.row.trade_discount" disable color="grey">
            </q-checkbox>
          </div>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
import usedownloadFile from 'src/composables/usedownloadFile'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  setup() {
    const metaData = {
      title: 'Purchase Discounts | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/purchase-discount/'
    const listData = useList(endpoint)
    const onDownloadXls = () => {
      useApi('v1/sales-voucher/export')
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.ms-excel',
            'Credit_Notes'
          )
        )
        .catch((err) => console.log('Error Due To', err))
    }
    const newColumn = [
      {
        name: 'voucher_no',
        label: 'Name.',
        align: 'left',
        field: 'name',
      },
      { name: 'type', label: 'Type', align: 'left', field: 'type' },
      { name: 'value', label: 'Value', align: 'left', field: 'value' },
      {
        name: 'trade_discount',
        label: 'Trade Discount',
        align: 'center',
        field: 'trade_discount',
      },
      { name: 'actions', label: 'Actions', align: 'left' },
    ]

    return { ...listData, onDownloadXls, newColumn, checkPermissions }
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
  width: 100px;
  flex-grow: 0;
  flex-shrink: 0;
}
</style>
