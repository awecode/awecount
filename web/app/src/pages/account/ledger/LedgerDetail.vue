<template>
  <div class="q-py-lg q-pl-lg q-mr-xl">
    <div class="text-h4 text-bold">{{ fields?.name || '-' }}</div>
    <div>
      <q-card class="q-mt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Code</div>
                <div class="q-px-md">{{ fields?.code || '-' }}</div>
              </div>
              <hr />
            </div>
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Dr Amount</div>
                <div class="q-px-md">{{ fields?.amounts?.dr || '-' }}</div>
              </div>
              <hr />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Category</div>
                <div class="q-px-md">{{ fields?.category_name || '-' }}</div>
              </div>
              <hr />
            </div>
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Cr Amount</div>
                <div class="q-px-md">{{ fields?.amounts?.cr || '-' }}</div>
              </div>
              <hr />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Parent</div>
                <div class="q-px-md">{{ fields?.parent_id || '-' }}</div>
              </div>
            </div>
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Closing Balance</div>
                <div class="q-px-md">{{ fields?.closing_balance || '-' }}</div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
      <div>
        <div class="text-h5 text-bold q-py-md">Transactions</div>
        <div class="row q-col-gutter-md">
          <DateRangePicker
            v-model:startDate="startDate"
            v-model:endDate="endDate"
            :hide-btns="true"
          />
          <div v-if="startDate != null || endDate != null">
            <q-btn
              @click.prevent="resetDate"
              square
              color="red"
              icon="fa-solid fa-xmark"
              class="q-mt-md"
            />
          </div>
          <div>
            <q-btn
              @click.prevent="filter"
              color="primary"
              label="FILTER"
              class="q-mt-md"
            />
          </div>
        </div>
      </div>
      <transaction-table :fields="fields"></transaction-table>
      <!-- <q-table
        :columns="columnList"
        :rows="rows"
        :loading="loading"
        v-model:pagination="pagination"
        row-key="id"
        @request="onRequest"
        class="q-mt-lg"
        :binary-state-sort="true"
        :rows-per-page-options="[]"
      >
        <template v-slot:body-cell-against="props">
          <q-td :props="props">
            <div v-for="account in props.row.accounts" :key="account.id">
              <router-link
                v-if="account.id !== fields.id"
                :to="`/account/${account.id}/view/`"
                style="font-weight: 500; text-decoration: none"
                class="text-blue"
                :title="`${account.name}`"
              >
                {{ account.name }}
              </router-link>
            </div>
          </q-td>
        </template>
        <template v-slot:body-cell-voucher_no="props">
          <q-td :props="props">
            <router-link
              :to="getVoucherUrl(props.row)"
              style="font-weight: 500; text-decoration: none"
              class="text-blue"
              >{{ props.row.voucher_no }}</router-link
            >
          </q-td>
        </template>
      </q-table> -->
    </div>
  </div>
</template>

<script setup>
import useApi from 'src/composables/useApi'
import { withQuery } from 'ufo'
const fields = ref(null)
const route = useRoute()
const router = useRouter()
const $q = useQuasar()

watch(
  route,
  () => {
    const url = `/v1/accounts/${route.params.id}/transactions/?`
    const updatedEndpoint = withQuery(url, route.query)
    endpoint.value = updatedEndpoint
  },
  {
    deep: true,
  }
)

const startDate = ref(null)
const endDate = ref(null)
const resetDate = () => {
  startDate.value = null
  endDate.value = null
  endpoint.value = `/v1/accounts/${route.params.id}/transactions/`
}
const filter = () => {
  if (!startDate.value || !endDate.value) {
    $q.notify({
      color: 'negative',
      message: 'Date Range not set!',
      icon: 'report_problem',
    })
  } else {
    // endpoint.value = `/v1/accounts/${route.params.id}/transactions/?start_date=${startDate.value}&end_date=${endDate.value}`
    router.push(
      `/account/${route.params.id}/view/?start_date=${startDate.value}&end_date=${endDate.value}`
    )
  }
}

const endpoint = ref(
  withQuery(`/v1/accounts/${route.params.id}/transactions/`, route.query)
)

const getData = () =>
  useApi(endpoint.value).then((data) => {
    fields.value = data
  })
getData()
watch(endpoint, () => getData())

const pagination = ref()
const loading = ref(false)
const initiallyLoaded = ref(false)
const rows = ref([])
// const columnList = ref([])

function loadData() {
  loading.value = true
  // const field = fields.value.transactions.results.value
  //   ? Object.keys(fields.value?.transactions?.results[0])?.filter((f) => {
  //       console.log('loop')
  //       f !== 'id'
  //     })
  //   : null
  // console.log(field)
  // columnList.value = field?.map((f) => {
  //   return {
  //     name: f,
  //     label: 'Name',
  //     align: 'left',
  //     field: f,
  //   }
  // })
  // columnList.value = [
  //   {
  //     name: 'date',
  //     label: 'Date',
  //     align: 'left',
  //     field: 'date',
  //   },
  //   {
  //     name: 'source_type',
  //     label: 'Voucher Type',
  //     align: 'left',
  //     field: 'source_type',
  //   },
  //   {
  //     name: 'against',
  //     label: 'Against',
  //     align: 'left',
  //     field: 'accounts',
  //   },
  //   {
  //     name: 'voucher_no',
  //     label: 'Voucher No.',
  //     align: 'left',
  //     field: 'voucher_no',
  //   },
  //   {
  //     name: 'dr',
  //     label: 'Dr.',
  //     align: 'left',
  //     field: 'dr_amount',
  //   },
  //   {
  //     name: 'cr',
  //     label: 'Cr.',
  //     align: 'left',
  //     field: 'cr_amount',
  //   },
  // ]

  rows.value = fields.value?.transactions?.results
  initiallyLoaded.value = true
  pagination.value = {
    page: fields.value?.transactions?.pagination?.page,
    rowsPerPage: fields.value?.transactions?.pagination?.size,
    rowsNumber: fields.value?.transactions?.pagination?.count,
  }
  loading.value = false
}

// function onRequest(prop) {
//   endpoint.value = `/v1/account/${route.params.id}/transactions/?${
//     startDate.value && endDate.value
//       ? 'start_date=' + startDate.value + '&end_date=' + endDate.value
//       : ''
//   }${
//     startDate.value && endDate.value
//       ? '&page=' + prop.pagination.page
//       : 'page=' + prop.pagination.page
//   }`
//   getData()
// }
onMounted(() => {
  if (route.query.start_date) {
    startDate.value = route.query.start_date
  }
  if (route.query.end_date) {
    endDate.value = route.query.end_date
  }
})

// TODO: Do clean up
</script>

<style>
hr {
  border-color: azure;
}
</style>
