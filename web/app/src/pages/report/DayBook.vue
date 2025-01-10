<script setup>
const route = useRoute()
const router = useRouter()

const date = ref(
  route.query.date ? route.query.date : new Date().toISOString().slice(0, 10)
)

const data = ref(null)

async function fetchData() {
  const res = await useApi('/v1/transaction/day-book?date=' + date.value)
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
      return (
        item.account.code
          .toLowerCase()
          .includes(searchQuery.value.toLowerCase()) ||
        item.account.name
          .toLowerCase()
          .includes(searchQuery.value.toLowerCase())
      )
    })
  }
  return data.value
}
</script>

<template>
  <div>
    <div class="q-pa-md">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-semibold">Day Book</h1>
      </div>
      <div>
        <DatePicker v-model="date" class="col-6" label="Date" />

        <div class="mt-4">
          <div v-if="data">
            <q-table
              :rows="data"
              :columns="columns"
              flat
              bordered
              hide-pagination
              :rows-per-page-options="[0]"
              :filter="searchQuery"
              :filter-method="filterData"
            >
              <template v-slot:top>
                <div class="search-bar">
                  <q-input
                    dense
                    debounce="500"
                    v-model="searchQuery"
                    placeholder="Search"
                    class="full-width search-input"
                  >
                    <template v-slot:append>
                      <q-icon name="search" />
                    </template>
                  </q-input>
                </div>
              </template>
              <template v-slot:body-cell-code="props">
                <q-td>
                  {{ props.row.account.code }}
                </q-td>
              </template>
              <template v-slot:body-cell-name="props">
                <q-td>
                  {{ props.row.account.name }}
                </q-td>
              </template>
              <template v-slot:body-cell-opening_balance="props">
                <q-td>
                  {{ props.row.opening_balance >= 0 ? 'Dr' : 'Cr' }}
                  {{ Math.abs(props.row.opening_balance).toFixed(2) }}
                </q-td>
              </template>
              <template v-slot:body-cell-closing_balance="props">
                <q-td>
                  {{ props.row.closing_balance >= 0 ? 'Dr' : 'Cr' }}
                  {{ Math.abs(props.row.closing_balance).toFixed(2) }}
                </q-td>
              </template>
              <template v-slot:body-cell-transaction="props">
                <q-td>
                  {{
                    (
                      props.row.opening_balance - props.row.closing_balance
                    ).toFixed(2)
                  }}
                </q-td>
              </template>
              <template v-slot:body-cell-action="props">
                <q-td>
                  <RouterLink
                    style="text-decoration: none"
                    class="text-blue-6"
                    target="_blank"
                    :to="`/account/${props.row.account.id}/view/?start_date=${date}&end_date=${date}`"
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
