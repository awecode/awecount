<script setup lang="ts">
import type { Ref } from 'vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
interface RowDataType {
  name: string
  net_amount: number
  discount_amount: number
  tax_amount: number
  quantity: number
}
const rows: Ref<Array<RowDataType>> = ref([])
const metaData = {
  title: 'Sales By Category | Awecount',
}
const fields: Ref<Record<string, string>> = ref({
  start_date: '',
  end_date: '',
})
useMeta(metaData)
const newColumn = [
  {
    name: 'category',
    label: 'Category',
    align: 'left',
    field: 'item__category__name',
    sortable: true,
  },
  {
    name: 'Total Quantity',
    label: 'Total Quantity',
    align: 'left',
    field: 'quantity',
    sortable: true,
  },
  {
    name: 'tax_amount',
    label: 'Total Tax',
    align: 'left',
    field: (row: Record<string, number>) => $nf(row.tax_amount),
    sortable: true,
  },
  {
    name: 'discount_amount',
    label: 'Total Discount',
    align: 'left',
    field: (row: Record<string, number>) => $nf(row.discount_amount),
    sortable: true,
  },
  {
    name: 'net_amount',
    label: 'Net Amount',
    align: 'left',
    field: (row: Record<string, number>) => $nf(row.net_amount),
    sortable: true,
  },
]
const updateRouteUrl = () => {
  let url = '/report/sales-by-category/'
  if (fields.value.start_date && fields.value.end_date) {
    url = `/report/sales-by-category/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
  }
  router.push(url)
}
const fetchData = () => {
  loading.value = true
  let endpoint = ''
  if (fields.value.start_date && fields.value.end_date) {
    endpoint = `v1/sales-row/by-category/?start_date=${fields.value.start_date}&end_date=${fields.value.end_date}`
    updateRouteUrl()
  } else {
    endpoint = 'v1/sales-row/by-category/'
  }
  useApi(endpoint, { method: 'GET' })
    .then((data) => {
      if (data.length > 2) {
        rows.value = data.sort((a: Record<string, number>, b: Record<string, number>) => b.item__category - a.item__category)
      } else {
        rows.value = data
      }
      loading.value = false
    })
    .catch((error) => {
      console.log(error)
      loading.value = false
    })
}
if (route.query.start_date) {
  fields.value.start_date = route.query.start_date as string
}
if (route.query.end_date) {
  fields.value.end_date = route.query.end_date as string
}
fetchData()
</script>

<template>
  <div class="q-pa-md">
    <div class="flex items-center justify-between gap-2">
      <div class="flex gap-x-6 gap-y-2 items-center">
        <div>
          <DateRangePicker v-model:end-date="fields.end_date" v-model:start-date="fields.start_date" :hide-btns="true" />
        </div>
        <q-btn
          v-if="fields.start_date || fields.end_date"
          class="f-reset-btn"
          color="red"
          icon="close"
          @click="
            fields = { start_date: '', end_date: '' }
            updateRouteUrl()
            fetchData()
          "
        />
        <q-btn
          class="f-submit-btn"
          color="green"
          label="fetch"
          :disable="!fields.start_date && !fields.end_date ? true : false"
          @click="fetchData"
        />
      </div>
    </div>
    <q-table
      class="q-mt-md"
      row-key="id"
      :columns="newColumn"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
    >
      <template #body-cell-category="props">
        <q-td :props="props">
          <span v-if="props.row.item__category__name" class="font-medium">{{ props.row.item__category__name }}</span>
          <span v-else class="font-medium text-gray-600">Uncategorized Items</span>
        </q-td>
      </template>
      <template #bottom-row>
        <q-td class="font-medium">
          Total
        </q-td>
        <q-td class="font-medium">
          {{ rows.reduce((accumulator, currentDict) => accumulator + currentDict.quantity, 0) }}
        </q-td>
        <q-td class="font-medium">
          {{ $nf(rows.reduce((accumulator, currentDict) => accumulator + currentDict.tax_amount, 0)) }}
        </q-td>
        <q-td class="font-medium">
          {{ $nf(rows.reduce((accumulator, currentDict) => accumulator + currentDict.discount_amount, 0)) }}
        </q-td>
        <q-td class="font-medium">
          {{ $nf(rows.reduce((accumulator, currentDict) => accumulator + currentDict.net_amount, 0)) }}
        </q-td>
      </template>
    </q-table>
  </div>
</template>

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
