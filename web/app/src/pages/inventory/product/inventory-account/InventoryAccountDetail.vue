<template>
  <div class="q-py-lg q-pl-lg q-mr-xl">
    <div class="row justify-between text-h4 text-bold">
      {{ fields?.name || '-' }}
      <q-btn :to="`/items/details/${route.params.id}/`" color="orange-6"
        >View Item</q-btn
      >
    </div>
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
                <div class="q-px-md text-grey-8">Current Balance</div>
                <div class="q-px-md">{{ fields?.current_balance || '-' }}</div>
              </div>
              <hr />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Category</div>
                <div class="q-px-md">{{ fields?.category || '-' }}</div>
              </div>
              <hr />
            </div>
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Opening Balance</div>
                <div class="q-px-md">{{ fields?.opening_balance || '-' }}</div>
              </div>
              <hr />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Parent</div>
                <div class="q-px-md">{{ fields?.parent || '-' }}</div>
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
          />
          <!-- <div v-if="startDate != null || endDate != null">
            <q-btn
              @click.prevent="resetDate"
              square
              color="red"
              icon="fa-solid fa-xmark"
              class="q-mt-md"
            />
          </div> -->
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
      <q-table
        :columns="columnList"
        :rows="rows"
        :loading="loading"
        v-model:pagination="pagination"
        row-key="id"
        @request="onRequest"
        class="q-mt-lg"
        :binary-state-sort="true"
        :rows-per-page-options="[20]"
      >
        <template v-slot:body-cell-accounts="props">
          <q-td :props="props">
            <router-link :to="`/account/${props.row.accounts[0].id}/view/`">{{
              props.row.accounts[0].name
            }}</router-link>
          </q-td>
        </template>
      </q-table>
    </div>
  </div>
</template>

<script setup>
import useApi from 'src/composables/useApi'
const fields = ref(null)
const route = useRoute()

// watch(route, () => {
//   endpoint.value = `/v1/inventory-account/${route.params.id}/transactions/`
//   getData()
// })
// const filters = ref({
//   start_date: null,
//   end_date: null,
// })
const startDate = ref(null)
const endDate = ref(null)
const resetDate = () => {
  startDate.value = null
  endDate.value = null
  endpoint.value = `/v1/inventory-account/${route.params.id}/transactions/`
}
const filter = () => {
  endpoint.value = `/v1/inventory-account/${route.params.id}/transactions/?start_date=${startDate.value}&end_date=${endDate.value}`
  getData()
}

const endpoint = ref(`/v1/inventory-account/${route.params.id}/transactions/`)

const getData = () =>
  useApi(endpoint.value).then((data) => {
    fields.value = data
    loadData()
  })
getData()

// watch(fields, () => {
//   loadData()
// })

const pagination = ref()
const loading = ref(false)
const initiallyLoaded = ref(false)
const rows = ref([])
const columnList = ref([])

function loadData() {
  loading.value = true
  const field = fields.value.transactions.results.value
    ? Object.keys(fields.value?.transactions?.results[0])?.filter(
        (f) => f !== 'id'
      )
    : null

  columnList.value = field?.map((f) => {
    return {
      name: f,
      label:
        f.replace(/_/g, ' ').charAt(0).toUpperCase() +
        f.replace(/_/g, ' ').slice(1),
      align: 'left',
      field: f,
    }
  })

  rows.value = fields.value?.transactions?.results
  initiallyLoaded.value = true
  pagination.value = {
    page: fields.value?.transactions?.pagination?.page,
    rowsPerPage: fields.value?.transactions?.pagination?.size,
    rowsNumber: fields.value?.transactions?.pagination?.count,
  }

  loading.value = false
}

function onRequest(prop) {
  endpoint.value = `/v1/inventory-account/${route.params.id}/transactions/?${
    startDate.value && endDate.value
      ? 'start_date=' + startDate.value + '&end_date=' + endDate.value
      : ''
  }${
    startDate.value && endDate.value
      ? '&page=' + prop.pagination.page
      : 'page=' + prop.pagination.page
  }`
  getData()
}
</script>
