<template>
  <div class="q-py-lg q-pl-lg q-mr-xl">
    <div class="flex justify-between">
      <div class="text-h5">
        <span class="text-bold">{{ fields?.name || '-' }}</span>
        <span v-if="fields?.category_name" class="q-ml-md text-h6 text-grey-7"> <q-tooltip>Category</q-tooltip> ({{
          fields?.category_name
          || '-' }})</span>
      </div>
      <div>
        <span v-if="fields?.code" class="ml-2 text-h6 text-grey-9 text-sm p-2 -mb-2 inline-block">[Code: {{
          fields?.code }}]</span>
      </div>
    </div>
    <div class="mt-8">
      <div class="grid lg:grid-cols-3 gap-x-6 gap-y-1">
        <div class="row justify-between q-py-sm b">
          <div class="q-px-md text-grey-8">Dr Amount</div>
          <div class="q-px-md">
            {{ $nf(fields?.amounts?.dr) || '-' }}
          </div>
        </div>

        <div class="row justify-between q-py-sm b">
          <div class="q-px-md text-grey-8">Cr Amount</div>
          <div class="q-px-md">{{ $nf(fields?.amounts?.cr) || '-' }}</div>
        </div>

        <div class="row justify-between q-py-sm b">
          <div class="q-px-md text-grey-8">Closing Balance</div>
          <div class="q-px-md">
            {{ $nf((fields?.amounts?.dr || 0) - (fields?.amounts?.cr || 0)) }}
          </div>
        </div>
      </div>
      <div class="sm:mt-6 mb-4 sm:mb-0 mt-2 px-2">
        <div class="row q-col-gutter-md print-hide">
          <DateRangePicker v-model:startDate="startDate" v-model:endDate="endDate" :hide-btns="true" />
          <div v-if="startDate != null || endDate != null">
            <q-btn @click.prevent="resetDate" square color="red" icon="fa-solid fa-xmark" class="q-mt-md" />
          </div>
          <div>
            <q-btn @click.prevent="filter" color="primary" label="FILTER" class="sm:q-mt-md" />
          </div>
        </div>
      </div>
      <transaction-table :fields="fields" v-if="fields?.transactions.results?.length > 0">
        <TablePagination :fields="fields"></TablePagination>
      </transaction-table>
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
  () => route.query,
  (newQuery, oldQuery) => {
    if (route.params.id && route.path.includes('/view/')) {
      const url = `/v1/accounts/${route.params.id}/transactions/`
      if (oldQuery.page !== newQuery.page) {
        const updatedEndpoint = withQuery(url, newQuery)
        endpoint.value = updatedEndpoint
      }
      if (oldQuery.pageSize !== newQuery.pageSize) {
        newQuery.page = undefined
        const updatedEndpoint = withQuery(url, newQuery)
        endpoint.value = updatedEndpoint
      }
      if (oldQuery.start_date !== newQuery.start_date || oldQuery.end_date !== newQuery.end_date) {
        newQuery.page = undefined
        const updatedEndpoint = withQuery(url, newQuery)
        endpoint.value = updatedEndpoint
      }
    }
  },
  {
    deep: true,
  }
)
watch(
  () => route.params.id,
  (newid) => {
    if (newid && route.path.includes('/view/')) {
      const url = `/v1/accounts/${route.params.id}/transactions/`
      const updatedEndpoint = withQuery(url, {})
      endpoint.value = updatedEndpoint
    }
  })
const startDate = ref(null)
const endDate = ref(null)
const resetDate = () => {
  startDate.value = null
  endDate.value = null
  router.push(`/account/${route.params.id}/view/`)
}
const filter = () => {
  if (!startDate.value || !endDate.value) {
    $q.notify({
      color: 'negative',
      message: 'Date Range not set!',
      icon: 'report_problem',
    })
  } else {
    router.push(
      `/account/${route.params.id}/view/?start_date=${startDate.value}&end_date=${endDate.value}`
    )
  }
}
const endpoint = ref(
  withQuery(`/v1/accounts/${route.params.id}/transactions/`, route.query)
)
const getData = () => {
  if (fields?.value?.transactions.results) fields.value.transactions.results = null
  useApi(endpoint.value).then((data) => {
    fields.value = data
    const metaData = {
      title: `${fields.value.name} | Account Detail | Awecount`,
    }
    useMeta(metaData)
  })
}
getData()
watch(endpoint, () => getData())
onMounted(() => {
  if (route.query.start_date) {
    startDate.value = route.query.start_date
  }
  if (route.query.end_date) {
    endDate.value = route.query.end_date
  }
})
</script>

<style scoped>
hr {
  border-color: azure;
}

@media print {

  td,
  th {
    padding: 5px;
    margin: 0;
    font-size: 12px !important;
    height: inherit !important;
  }

  .q-card {
    box-shadow: none;
  }
}
</style>
