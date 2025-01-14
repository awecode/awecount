<script setup>
const route = useRoute()
const router = useRouter()

const date = ref(route.query.date ? route.query.date : new Date().toISOString().slice(0, 10))

const data = ref(null)

async function fetchData() {
  const res = await useApi(`/api/company/${route.params.company}/transaction/day-book?date=${date.value}`)
  data.value = res
}

fetchData()

watch(date, () => {
  router.push({
    query: {
      ...route.query,
      date: date.value,
    },
  })
  fetchData()
})

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
    sortable: true,
  },
  {
    name: 'transaction',
    label: 'Transaction',
    align: 'left',
    field: 'transaction',
    sortable: true,
  },
  {
    name: 'closing_balance',
    label: 'Closing Balance',
    align: 'left',
    field: 'closing_balance',
    sortable: true,
  },
  { name: 'action', label: '', align: 'left' },
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
        <DatePicker v-model="date" class="col-6" label="Date" />

        <div class="mt-4">
          <div v-if="data">
            <q-table
              bordered
              flat
              hide-pagination
              :columns="columns"
              :filter="searchQuery"
              :filter-method="filterData"
              :rows="data"
              :rows-per-page-options="[0]"
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
                    style="text-decoration: none"
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
