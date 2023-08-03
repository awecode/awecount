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
                <div class="q-px-md">{{ (fields?.amounts?.dr || 0) - (fields?.amounts?.cr || 0) }}</div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
      <div>
        <div class="text-h5 text-bold q-py-md">Transactions</div>
        <div class="row q-col-gutter-md">
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
        <div class="row justify-end items-center" v-if="fields.transactions?.pagination.pages > 0">
          <div class="q-mr-sm">
            <span>
              {{ (fields.transactions?.pagination.page - 1) * 20 + 1 }} -
              {{
                fields.transactions?.pagination.page ===
                fields.transactions?.pagination.pages
                ? fields.transactions?.pagination.count
                : (fields.transactions?.pagination.page - 1) * 20 +
                fields.transactions?.pagination.size
              }}
            </span>
            <span>&nbsp; of &nbsp;{{ fields.transactions?.pagination.count }}</span>
          </div>
          <q-btn icon="first_page" dense flat round :disable="fields.transactions?.pagination.page === 1"
            @click="() => goToPage(1)"></q-btn>
          <q-btn icon="chevron_left" dense flat round :disable="fields.transactions?.pagination.page === 1"
            @click="() => goToPage(fields.transactions?.pagination.page - 1)"></q-btn>
          <q-btn icon="chevron_right" dense flat round :disable="fields.transactions?.pagination.page ===
            fields.transactions?.pagination.pages
            " @click="() => goToPage(fields.transactions?.pagination.page + 1)"></q-btn>
          <q-btn icon="last_page" dense flat round :disable="fields.transactions?.pagination.page ===
            fields.transactions?.pagination.pages
            " @click="() => goToPage(fields.transactions?.pagination.pages)"></q-btn>
        </div>
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
const metaData = {
  title: 'Account Detail | Awecount',
}
useMeta(metaData)
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
  })
getData()
watch(endpoint, () => getData())
function goToPage(pageNo) {
  let newQuery = Object.assign({ ...route.query }, { page: pageNo })
  router.push(withQuery(`/account/${route.params.id}/view/`, newQuery))
}
onMounted(() => {
  if (route.query.start_date) {
    startDate.value = route.query.start_date
  }
  if (route.query.end_date) {
    endDate.value = route.query.end_date
  }
})
</script>

<style>
hr {
  border-color: azure;
}
</style>
