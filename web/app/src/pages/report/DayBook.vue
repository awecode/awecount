<script setup>
const route = useRoute()
const router = useRouter()
const viewTransactionOnly = ref(false)
const salesData = ref(null)
const purchaseData = ref(null)
const salesPagination = ref({
  page: 1,
  rowsPerPage: 20,
  rowsNumber: 0,
})
const salesPage = ref(1)
const purchasePagination = ref({
  page: 1,
  rowsPerPage: 20,
  rowsNumber: 0,
})
const purchasePage = ref(1)

const date = ref(route.query.date ? route.query.date : new Date().toISOString().slice(0, 10))

const data = ref(null)

async function fetchData() {
  const res = await useApi(`/api/company/${route.params.company}/transaction/day-book?date=${date.value}`)
  data.value = res
  viewTransactionOnly.value = false
}
async function fetchSalesData() {
  const res = await useApi(`/api/company/${route.params.company}/sales-voucher/?start_date=${date.value}&end_date=${date.value}&page=${salesPage.value}&status=Partially+Paid&status=Paid&status=Issued`)
  salesPagination.value = {
    page: res.pagination.page,
    rowsPerPage: res.pagination.size,
    rowsNumber: res.pagination.count,
  }
  salesData.value = res
}

async function fetchPurchaseData() {
  const res = await useApi(`/api/company/${route.params.company}/purchase-vouchers/?start_date=${date.value}&end_date=${date.value}&page=${purchasePage.value}&status=Partially+Paid&status=Paid&status=Issued`)
  purchaseData.value = res
}

const metaData = {
  title: 'Day Book | Awecount',
}
useMeta(metaData)

fetchData()
fetchSalesData()
fetchPurchaseData()

watch(date, () => {
  router.push({
    query: {
      ...route.query,
      date: date.value,
    },
  })
  salesPage.value = 1
  purchasePage.value = 1
  fetchData()
  fetchSalesData()
  fetchPurchaseData()
})
const salesColumns = [
  {
    name: 'voucher_no',
    label: 'Voucher no',
    align: 'left',
    field: 'voucher_no',
  },
  {
    name: 'party_name',
    label: 'Party name',
    align: 'left',
    field: 'party_name',
  },
  {
    name: 'date',
    label: 'Date',
    align: 'left',
    field: 'date',
  },
  { name: 'status', label: 'Status', align: 'left', field: 'status' },
  {
    name: 'payment_mode',
    label: 'Payment Mode',
    align: 'left',
    field: 'payment_mode',
  },
  {
    name: 'total_amount',
    label: 'Total amount',
    align: 'left',
    field: 'total_amount',
  },
]
const purchaseColumns = [
  {
    name: 'voucher_no',
    label: 'Bill No.',
    align: 'left',
    field: 'voucher_no',
    sortable: true,
  },
  {
    name: 'party_name',
    label: 'Party',
    align: 'left',
    field: 'party',
  },
  { name: 'status', label: 'Status', align: 'left', field: 'status' },
  { name: 'date', label: 'Date', align: 'left', field: 'date' },
  {
    name: 'payment_mode',
    label: 'Payment Mode',
    align: 'left',
    field: 'payment_mode',
  },
  {
    name: 'total_amount',
    label: 'Total amount',
    align: 'left',
    field: 'total_amount',
  },
]
const columns = [
  {
    name: 'code',
    label: 'Account Code',
    align: 'left',
    field: 'account.code',
  },
  {
    name: 'name',
    label: 'Account Name',
    align: 'left',
    field: 'account.name',
  },
  {
    name: 'opening_balance',
    label: 'Opening Balance',
    align: 'left',
    field: 'opening_balance',
  },
  {
    name: 'transaction',
    label: 'Transaction',
    align: 'left',
    field: 'transaction',
  },
  {
    name: 'closing_balance',
    label: 'Closing Balance',
    align: 'left',
    field: 'closing_balance',
  },
]

const searchQuery = ref(route.query.search ? route.query.search : '')

watch(searchQuery, () => {
  router.push({
    query: {
      ...route.query,
      search: searchQuery.value || undefined,
    },
  })
})

function filterData() {
  if (searchQuery.value) {
    return data.value.filter((item) => {
      return item.account.code.toLowerCase().includes(searchQuery.value.toLowerCase()) || item.account.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    })
  }
  return data.value
}
function filterTransactionData() {
  if (viewTransactionOnly.value) {
    data.value = data.value.filter((item) => {
      return item.has_transactions
    })
  } else {
    fetchData()
  }
}
function onSalesRequest(props) {
  salesPage.value = props.pagination.page
  fetchSalesData()
}
function onPurchaseRequest(props) {
  purchasePage.value = props.pagination.page
  fetchPurchaseData()
}
</script>

<template>
  <div>
    <div class="q-pa-md">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-semibold">
          Day Book
        </h1>
      </div>
      <div>
        <div class="flex flex-col gap-10">
          <div class="flex gap-12 col-6">
            <DatePicker v-model="date" class="grow" label="Date" />
            <q-checkbox
              v-model="viewTransactionOnly"
              class="mr-10"
              label="Show Transaction only"
              @click="filterTransactionData"
            />
          </div>
          <div class="grid grid-cols-2 gap-10">
            <div class="flex flex-col gap-2">
              <div class="flex flex-col gap-3">
                <div class="text-xl">
                  Sales Data
                </div>
                <div v-if="salesData?.results">
                  <q-table
                    v-model:pagination="salesPagination"
                    bordered
                    flat
                    :columns="salesColumns"
                    :rows="salesData?.results"
                    :rows-per-page-options="[12]"
                    @request="onSalesRequest"
                  >
                    <template #body-cell-voucher_no="props">
                      <q-td :props="props">
                        <router-link
                          class="text-blue"
                          style="font-weight: 500; text-decoration: none"
                          target="_blank"
                          :to="`/sales-voucher/${props.row.id}/view`"
                        >
                          {{ props.row.voucher_no }}
                        </router-link>
                      </q-td>
                    </template>
                  </q-table>
                </div>
                <div v-if="salesData?.results?.length && salesData?.pagination?.pages === 1" class="flex justify-end gap-4 mr-4">
                  <div>Total Sales:</div>
                  <div class="font-semibold">
                    {{
                      salesData.results
                        ?.reduce((acc, cur) => {
                          return acc + cur.total_amount
                        }, 0)
                        .toFixed(2)
                    }}
                  </div>
                </div>
              </div>
            </div>
            <div class="flex flex-col gap-2">
              <div class="flex flex-col gap-3">
                <div class="text-xl">
                  Purchase Data
                </div>
                <div v-if="purchaseData?.results" class="flex flex-col gap-3">
                  <q-table
                    v-model:pagination="purchasePagination"
                    bordered
                    flat
                    :columns="purchaseColumns"
                    :rows="purchaseData?.results"
                    :rows-per-page-options="[20]"
                    @request="onPurchaseRequest"
                  >
                    <template #body-cell-voucher_no="props">
                      <q-td :props="props">
                        <router-link
                          class="text-blue"
                          style="font-weight: 500; text-decoration: none"
                          target="_blank"
                          :to="`/purchase-voucher/${props.row.id}/view`"
                        >
                          {{ props.row.voucher_no }}
                        </router-link>
                      </q-td>
                    </template>
                  </q-table>
                </div>
                <div v-if="purchaseData?.results.length" class="flex justify-end gap-4 mr-4">
                  <div>Total Purchase:</div>
                  <div class="font-semibold">
                    {{
                      purchaseData?.results
                        ?.reduce((acc, cur) => {
                          return acc + cur.total_amount
                        }, 0)
                        .toFixed(2)
                    }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4">
          <div v-if="data">
            <q-table
              bordered
              flat
              :columns="columns"
              :filter="searchQuery"
              :filter-method="filterData"
              :rows="data"
              :rows-per-page-options="[20]"
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
                </div>
              </template>
              <template #body-cell-code="props">
                <q-td>
                  {{ props.row.account.code }}
                </q-td>
              </template>
              <template #body-cell-name="props">
                <q-td>
                  {{ props.row.account.name }}
                </q-td>
              </template>
              <template #body-cell-opening_balance="props">
                <q-td>
                  {{ props.row.opening_balance >= 0 ? 'Dr' : 'Cr' }}
                  {{ Math.abs(props.row.opening_balance).toFixed(2) }}
                </q-td>
              </template>
              <template #body-cell-closing_balance="props">
                <q-td>
                  {{ props.row.closing_balance >= 0 ? 'Dr' : 'Cr' }}
                  {{ Math.abs(props.row.closing_balance).toFixed(2) }}
                </q-td>
              </template>
              <template #body-cell-transaction="props">
                <q-td>
                  {{ (props.row.opening_balance - props.row.closing_balance).toFixed(2) }}
                </q-td>
              </template>
              <template #body-cell-action="props">
                <q-td>
                  <RouterLink
                    class="text-blue-6"
                    style="text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
                    target="_blank"
                    :to="`/${$route.params.company}/account/${props.row.account.id}/view/?start_date=${date}&end_date=${date}`"
                  >
                    View Transactions
                  </RouterLink>
                </q-td>
              </template>
            </q-table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
