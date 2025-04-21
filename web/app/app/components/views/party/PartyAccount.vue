<script lang="ts">
import type { Ref } from 'vue'
import TransactionTable from '@/components/account/TransactionTable.vue'
import useApi from '@/composables/useApi'
import { withQuery } from 'ufo'
import { useRoute, useRouter } from 'vue-router'

export default defineNuxtComponent({
  setup() {
    const metaData = {
      title: 'Party Account | Awecount',
    }
    useHead(metaData)
    const router = useRouter()
    const route = useRoute()
    const $q = useQuasar()
    interface Amounts {
      dr: number
      cr: number
    }
    interface Fields {
      customer_account: Record<string, string | number | Amounts> | null
      name: string
      supplier_account: Record<string, string | number | Amounts> | null
    }
    const fields: Ref<null | Fields> = ref(null)
    interface DateRef {
      start_date: string | null
      end_date: string | null
    }
    const dateRef: Ref<DateRef> = ref({
      start_date: null,
      end_date: null,
    })
    const endpoint = ref(withQuery(`/api/company/${route.params.company}/parties/${route.params.id}/transactions/`, route.query))
    function fetchData() {
      if (fields?.value?.transactions.results) fields.value.transactions.results = null
      useApi(endpoint.value, { method: 'GET' })
        .then((data) => {
          fields.value = data
        })
        .catch((error) => {
          if (error.response && error.response.status == 404) {
            router.replace({ path: '/ErrorNotFound' })
          }
        })
    }
    const resetDate = () => {
      dateRef.value = { start_date: null, end_date: null }
      router.push(`/${route.params.company}/crm/parties/${route.params.id}/account`)
    }
    watch(endpoint, () => fetchData())
    watch(
      () => route.query,
      (newQuery, oldQuery) => {
        if (route.params.id && route.path.includes('/parties/account/')) {
          const url = `/api/company/${route.params.company}/parties/${route.params.id}/transactions/?`
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
      },
    )
    watch(
      () => route.params.id,
      (newid) => {
        if (newid && route.path.includes('/parties/account/')) {
          const url = `/api/company/${route.params.company}/parties/${newid}/transactions/?`
          const updatedEndpoint = withQuery(url, {})
          endpoint.value = updatedEndpoint
        }
      },
    )
    const filter = () => {
      if (!dateRef.value.start_date || !dateRef.value.end_date) {
        $q.notify({
          color: 'negative',
          message: 'Date Range not set!',
          icon: 'report_problem',
        })
      } else {
        router.push(`/${route.params.company}/crm/parties/${route.params.id}/account?start_date=${dateRef.value.start_date}&end_date=${dateRef.value.end_date}`)
      }
    }
    return {
      fields,
      // journalQueryFilter,
      TransactionTable,
      fetchData,
      dateRef,
      resetDate,
      endpoint,
      filter,
    }
  },
  created() {
    if (this.$route.query.start_date && this.$route.query.end_date) {
      this.dateRef = {
        start_date: this.$route.query.start_date,
        end_date: this.$route.query.end_date,
      }
    }
    useApi(this.endpoint, { method: 'GET' })
      .then((data) => {
        this.fields = data
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ path: '/ErrorNotFound' })
        }
      })
  },
})
</script>

<template>
  <div v-if="fields" class="q-pa-md">
    <q-card>
      <h5 class="bg-grey-4 q-pa-md q-ma-none">
        {{ fields?.name }}
      </h5>
      <q-markup-table>
        <thead>
          <tr>
            <th class="text-left">
              Account
            </th>
            <th class="text-left">
              Code
            </th>
            <th class="text-left">
              Dr
            </th>
            <th class="text-left">
              Cr
            </th>
            <th class="text-left">
              Balance
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="fields.supplier_account && (fields.supplier_account.amounts.dr != null || fields.supplier_account.amounts.cr != null)">
            <td class="text-left">
              <router-link class="text-blue" style="text-decoration: none" :to="`/${$route.params.company}/account/ledgers/${fields.supplier_account?.id}`">
                Vendor (Payable)
              </router-link>
            </td>
            <td class="text-left">
              {{ fields.supplier_account.code }}
            </td>
            <td class="text-left">
              {{ $nf(fields.supplier_account.amounts.dr, 2) }}
            </td>
            <td class="text-left">
              {{ $nf(fields.supplier_account.amounts.cr, 2) }}
            </td>
            <td class="text-left">
              {{ $nf((fields.supplier_account.amounts.dr || 0) - (fields.supplier_account.amounts.cr || 0), 2) }}
            </td>
          </tr>
          <tr v-if="fields.customer_account && (fields.customer_account.amounts.dr != null || fields.customer_account.amounts.cr != null)">
            <td class="text-left">
              <router-link class="text-blue" style="text-decoration: none" :to="`/${$route.params.company}/account/ledgers/${fields.customer_account?.id}`">
                Customer (Receivable)
              </router-link>
            </td>
            <td class="text-left">
              {{ fields.customer_account.code }}
            </td>
            <td class="text-left">
              {{ $nf(fields.customer_account.amounts.dr, 2) }}
            </td>
            <td class="text-left">
              {{ $nf(fields.customer_account.amounts.cr, 2) }}
            </td>
            <td class="text-left">
              {{ $nf((fields.customer_account.amounts.dr || 0) - (fields.customer_account.amounts.cr || 0), 2) }}
            </td>
          </tr>
          <tr v-if="fields.supplier_account && fields.customer_account">
            <td colspan="2"></td>
            <th class="text-left">
              {{ $nf((fields.supplier_account.amounts.dr || 0) + (fields.customer_account.amounts.dr || 0), 2) }}
            </th>
            <th class="text-left">
              {{ $nf((fields.supplier_account.amounts.cr || 0) + (fields.customer_account.amounts.cr || 0), 2) }}
            </th>
            <th class="text-left">
              {{ $nf((fields.supplier_account.amounts.dr || 0) - (fields.supplier_account.amounts.cr || 0) + (fields.customer_account.amounts.dr || 0) - (fields.customer_account.amounts.cr || 0), 2) }}
            </th>
          </tr>
        </tbody>
      </q-markup-table>
    </q-card>
    <q-card class="q-mt-md q-pa-md">
      <h5 class="q-ma-none">
        Transactions
      </h5>
      <div class="row items-center q-mx-sm print-hide">
        <DateRangePicker
          v-model:end-date="dateRef.end_date"
          v-model:start-date="dateRef.start_date"
          class="q-mr-md"
          :hide-btns="true"
        />
        <span class="row items-end q-gutter-y-sm">
          <q-btn
            v-if="dateRef.start_date && dateRef.end_date"
            class="q-mr-sm"
            color="red"
            icon="close"
            @click="resetDate"
          />
          <q-btn
            color="blue"
            label="filter"
            :disable="!(dateRef.start_date && dateRef.end_date)"
            @click="filter"
          />
        </span>
      </div>
      <TransactionTable v-if="fields?.transactions.results?.length > 0" :fields="fields">
        <TablePagination :fields="fields" />
      </TransactionTable>
    </q-card>
  </div>
</template>

<style scoped>
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
