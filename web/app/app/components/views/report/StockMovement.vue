<script setup>
useHead({
  title: 'Stock Movement Report',
})

const route = useRoute()

const endpoint = `/api/company/${route.params.company}/items/stock-movement/`

const { filters, resetFilters, onRequest, pagination, rows, loading, searchQuery, onFilterUpdate } = useList(endpoint)

const columns = [
  {
    name: 'item_description',
    label: 'Item Description',
    subColumns: [
      {
        name: 'code',
        field: 'code',
        label: 'Code',
        align: 'left',
        sortable: true,
      },
      {
        name: 'name',
        field: 'name',
        label: 'Name',
        align: 'left',
        sortable: true,
      },
      {
        name: 'unit',
        field: 'unit',
        label: 'Unit',
        align: 'center',
      },
    ],
  },
  {
    name: 'opening_balance',
    label: 'Opening Balance',
    subColumns: [
      {
        name: 'opening_qty',
        field: 'opening_qty',
        label: 'Quantity',
        align: 'right',
        sortable: true,
      },
      {
        name: 'opening_value',
        field: 'opening_value',
        label: 'Value',
        align: 'right',
        sortable: true,
      },
    ],
  },
  {
    name: 'purchase',
    label: 'Purchase',
    subColumns: [
      {
        name: 'purchase_qty',
        field: 'purchase_qty',
        label: 'Quantity',
        align: 'right',
        sortable: true,
      },
      {
        name: 'purchase_value',
        field: 'purchase_value',
        label: 'Value',
        align: 'right',
        sortable: true,
      },
    ],
  },
  {
    name: 'purchase_return',
    label: 'Purchase Return',
    subColumns: [
      {
        name: 'purchase_return_qty',
        field: 'purchase_return_qty',
        label: 'Quantity',
        align: 'right',
      },
      {
        name: 'purchase_return_value',
        field: 'purchase_return_value',
        label: 'Value',
        align: 'right',
      },
    ],
  },
  {
    name: 'sales',
    label: 'Sales',
    subColumns: [
      {
        name: 'sales_qty',
        field: 'sales_qty',
        label: 'Quantity',
        align: 'right',
        sortable: true,
      },
      {
        name: 'sales_value',
        field: 'sales_value',
        label: 'Value',
        align: 'right',
        sortable: true,
      },
    ],
  },
  {
    name: 'sales_return',
    label: 'Sales Return',
    subColumns: [
      {
        name: 'sales_return_qty',
        field: 'sales_return_qty',
        label: 'Quantity',
        align: 'right',
      },
      {
        name: 'sales_return_value',
        field: 'sales_return_value',
        label: 'Value',
        align: 'right',
      },
    ],
  },
  {
    name: 'stock_in',
    label: 'Stock In',
    subColumns: [
      {
        name: 'stock_in_qty',
        field: 'stock_in_qty',
        label: 'Quantity',
        align: 'right',
      },
      {
        name: 'stock_in_value',
        field: 'stock_in_value',
        label: 'Value',
        align: 'right',
      },
    ],
  },
  {
    name: 'stock_out',
    label: 'Stock Out',
    subColumns: [
      {
        name: 'stock_out_qty',
        field: 'stock_out_qty',
        label: 'Quantity',
        align: 'right',
      },
      {
        name: 'stock_out_value',
        field: 'stock_out_value',
        label: 'Value',
        align: 'right',
      },
    ],
  },
  {
    name: 'production',
    label: 'Production',
    subColumns: [
      {
        name: 'production_qty',
        field: 'production_qty',
        label: 'Quantity',
        align: 'right',
      },
      {
        name: 'production_value',
        field: 'production_value',
        label: 'Value',
        align: 'right',
      },
    ],
  },
  {
    name: 'consumption',
    label: 'Consumption',
    subColumns: [
      {
        name: 'consumption_qty',
        field: 'consumption_qty',
        label: 'Quantity',
        align: 'right',
      },
      {
        name: 'consumption_value',
        field: 'consumption_value',
        label: 'Value',
        align: 'right',
      },
    ],
  },
  {
    name: 'closing_stock',
    label: 'Closing Stock',
    subColumns: [
      {
        name: 'closing_qty',
        field: 'closing_qty',
        label: 'Quantity',
        align: 'right',
        sortable: true,
      },
      {
        name: 'closing_value',
        field: 'closing_value',
        label: 'Value',
        align: 'right',
        sortable: true,
      },
    ],
  },
]

const flattenedColumns = columns.reduce((acc, column) => {
  acc.push(...column.subColumns)
  return acc
}, [])

const exporting = ref(false)

const onExport = async () => {
  if (exporting.value) return
  exporting.value = true
  window.addEventListener('beforeunload', (event) => {
    event.preventDefault()
    event.returnValue = ''
  })
  try {
    const res = await useApi(`${endpoint}?start_date=${filters.value.start_date ?? ''}&end_date=${filters.value.end_date ?? ''}&export=true&type=xlsx&item_ids=${filters.value.item_ids ?? ''}`)

    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = 'Stock Movement Report.xlsx'
    link.click()
  } catch (error) {
    console.error(error)
  } finally {
    exporting.value = false
    window.removeEventListener('beforeunload', (event) => {
      event.preventDefault()
      event.returnValue = ''
    })
  }
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row q-mb-md justify-end">
      <q-btn
        color="primary"
        icon-right="download"
        label="Export"
        :loading="exporting"
        @click="onExport"
      />
      <q-btn
        flat
        round
        class="q-ml-md"
        icon="filter_list"
      >
        <q-menu>
          <div class="q-pa-md" style="min-width: 300px">
            <div class="text-h6 q-mb-md">
              Filters
            </div>
            <DateRangePicker v-model:end-date="filters.end_date" v-model:start-date="filters.start_date" />
            <div class="row q-gutter-sm q-mt-md">
              <q-btn color="primary" label="Apply" @click="onFilterUpdate" />
              <q-btn color="grey" label="Reset" @click="resetFilters" />
            </div>
          </div>
        </q-menu>
      </q-btn>
    </div>

    <q-table
      v-model:pagination="pagination"
      row-key="id"
      title="Stock Movement Report"
      :columns="flattenedColumns"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top></template>
      <template #header="props">
        <q-tr>
          <q-th v-for="col in columns" :key="col.name" :colspan="col.subColumns?.length || 1">
            {{ col.label }}
          </q-th>
        </q-tr>

        <q-tr :props="props">
          <q-th v-for="col in props.cols" :key="col.name" :props="props">
            {{ col.label }}
          </q-th>
        </q-tr>
      </template>
    </q-table>
  </div>
</template>
