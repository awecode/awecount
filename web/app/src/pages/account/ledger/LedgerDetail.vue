<template>
  <div class="q-py-lg q-pl-lg q-mr-xl">
    <div class="text-h5">
      <!-- <span v-if="fields?.code" class="q-ml-md text-grey-9 text-h5x"
        >{{ fields.code }}:
      </span> -->
      <span class="text-bold">{{ fields?.name || '-' }}</span>
      <span v-if="fields?.code" class="ml-2 text-h6 text-grey-9" title="Code">{{
        fields.code
      }}</span>
      <span
        v-if="fields?.category_name"
        class="q-ml-md text-h6 text-grey-7"
        title="Category"
        >({{ fields?.category_name || '-' }})</span
      >
    </div>
    <div class="mt-8">
      <!-- <q-card class="q-mt-md">
        <q-card-section> -->
      <div class="grid grid-cols-3 gap-x-24">
        <div
          class="row justify-between q-py-sm border-color-red border border-bottom-1 bg-gray-200"
        >
          <div class="q-px-md text-grey-8">Dr Amount</div>
          <div class="q-px-md">
            {{ $nf(fields?.amounts?.dr) || '-' }}
          </div>
        </div>

        <div class="row justify-between q-py-sm bg-gray-200">
          <div class="q-px-md text-grey-8">Cr Amount</div>
          <div class="q-px-md">{{ fields?.amounts?.cr || '-' }}</div>
        </div>

        <div class="row justify-between q-py-sm bg-gray-200">
          <div class="q-px-md text-grey-8">Closing Balance</div>
          <div class="q-px-md">
            {{ (fields?.amounts?.dr || 0) - (fields?.amounts?.cr || 0) }}
          </div>
        </div>
      </div>
      <!-- </q-card-section>
      </q-card> -->
      <div>
        <div class="text-h6 text-bold q-py-md">Transactions</div>
        <div class="row q-col-gutter-md print-hide">
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
      <transaction-table :fields="fields">
        <div
          class="row justify-end items-center"
          v-if="fields.transactions?.pagination.pages > 0"
        >
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
            <span
              >&nbsp; of &nbsp;{{ fields.transactions?.pagination.count }}</span
            >
          </div>
          <q-btn
            icon="first_page"
            dense
            flat
            round
            :disable="fields.transactions?.pagination.page === 1"
            @click="() => goToPage(1)"
          ></q-btn>
          <q-btn
            icon="chevron_left"
            dense
            flat
            round
            :disable="fields.transactions?.pagination.page === 1"
            @click="() => goToPage(fields.transactions?.pagination.page - 1)"
          ></q-btn>
          <q-btn
            icon="chevron_right"
            dense
            flat
            round
            :disable="
              fields.transactions?.pagination.page ===
              fields.transactions?.pagination.pages
            "
            @click="() => goToPage(fields.transactions?.pagination.page + 1)"
          ></q-btn>
          <q-btn
            icon="last_page"
            dense
            flat
            round
            :disable="
              fields.transactions?.pagination.page ===
              fields.transactions?.pagination.pages
            "
            @click="() => goToPage(fields.transactions?.pagination.pages)"
          ></q-btn>
        </div>
      </transaction-table>
    </div>
  </div>
</template>

<script setup>
import useApi from 'src/composables/useApi'
// import { $nf } from 'src/composables/global'
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
