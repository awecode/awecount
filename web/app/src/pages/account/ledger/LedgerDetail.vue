<template>
  <div class="q-py-lg q-pl-lg q-mr-xl">
    <div class="flex justify-between">
      <div class="text-h5">
        <!-- <span v-if="fields?.code" class="q-ml-md text-grey-9 text-h5x"
        >{{ fields.code }}:
      </span> -->
        <span class="text-bold">{{ fields?.name || '-' }}</span>
        <!-- <span v-if="fields?.code" class="ml-2 text-h6 text-grey-9" title="Code">{{
        fields.code
      }}</span> -->
        <span v-if="fields?.category_name" class="q-ml-md text-h6 text-grey-7" title="Category">({{ fields?.category_name
          || '-' }})</span>
      </div>
      <div>
        <span v-if="fields?.code" class="ml-2 text-h6 text-grey-9 text-sm p-2 -mb-2 inline-block" title="Code">[Code: {{
          fields.code }}]</span>
      </div>
    </div>
    <div class="mt-8">
      <!-- <q-card class="q-mt-md">
        <q-card-section> -->
      <div class="grid grid-cols-3 gap-x-6">
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
      <!-- </q-card-section>
      </q-card> -->
      <div class="mt-8 px-2">
        <div class="row q-col-gutter-md print-hide">
          <DateRangePicker v-model:startDate="startDate" v-model:endDate="endDate" :hide-btns="true" />
          <div v-if="startDate != null || endDate != null">
            <q-btn @click.prevent="resetDate" square color="red" icon="fa-solid fa-xmark" class="q-mt-md" />
          </div>
          <div>
            <q-btn @click.prevent="filter" color="primary" label="FILTER" class="q-mt-md" />
          </div>
        </div>
      </div>
      <transaction-table :fields="fields">
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
  route,
  () => {
    if (route.params.id) {
      const url = `/v1/accounts/${route.params.id}/transactions/?`
      const updatedEndpoint = withQuery(url, route.query)
      endpoint.value = updatedEndpoint
    }
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
const getData = () =>
  useApi(endpoint.value).then((data) => {
    fields.value = data
    const metaData = {
      title: `${fields.value.name} | Account Detail | Awecount`,
    }
    useMeta(metaData)
  })
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
