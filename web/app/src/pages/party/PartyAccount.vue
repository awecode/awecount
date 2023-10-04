<template>
  <div class="q-pa-md" v-if="fields">
    <q-card>
      <h5 class="bg-grey-4 q-pa-md q-ma-none">
        {{ fields?.name }}
      </h5>
      <q-markup-table>
        <thead>
          <tr>
            <th class="text-left">Account</th>
            <th class="text-left">Code</th>
            <th class="text-left">Dr</th>
            <th class="text-left">Cr</th>
            <th class="text-left">Balance</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="fields.supplier_account &&
            (fields.supplier_account.amounts.dr != null ||
              fields.supplier_account.amounts.cr != null)
            ">
            <td class="text-left">
              <router-link :to="`/account/${fields.supplier_account?.id}/view/`" class="text-blue"
                style="text-decoration: none">
                Vendor (Payable)
              </router-link>
            </td>
            <td class="text-left">{{ fields.supplier_account.code }}</td>
            <td class="text-left">
              {{ $nf(fields.supplier_account.amounts.dr, 2) }}
            </td>
            <td class="text-left">
              {{ $nf(fields.supplier_account.amounts.cr, 2) }}
            </td>
            <td class="text-left">
              {{
                $nf((fields.supplier_account.amounts.dr || 0) -
                  (fields.supplier_account.amounts.cr || 0), 2)
              }}
            </td>
          </tr>
          <tr v-if="fields.customer_account &&
              (fields.customer_account.amounts.dr != null ||
                fields.customer_account.amounts.cr != null)
              ">
            <td class="text-left">
              <router-link :to="`/account/${fields.customer_account?.id}/view/`" class="text-blue"
                style="text-decoration: none">
                Customer (Receivable)
              </router-link>
            </td>
            <td class="text-left">{{ fields.customer_account.code }}</td>
            <td class="text-left">
              {{ $nf(fields.customer_account.amounts.dr, 2) }}
            </td>
            <td class="text-left">
              {{ $nf(fields.customer_account.amounts.cr, 2) }}
            </td>
            <td class="text-left">
              {{
                $nf((fields.customer_account.amounts.dr || 0) -
                  (fields.customer_account.amounts.cr || 0), 2)
              }}
            </td>
          </tr>
          <tr v-if="fields.supplier_account && fields.customer_account">
            <td colspan="2"></td>
            <th class="text-left">
              {{
                $nf(fields.supplier_account.amounts.dr ||
                  0 + fields.customer_account.amounts.dr ||
                  0, 2)
              }}
            </th>
            <th class="text-left">
              {{
                $nf(fields.supplier_account.amounts.cr ||
                  0 + fields.customer_account.amounts.cr ||
                  0, 2)
              }}
            </th>
            <th class="text-left">
              {{
                $nf((fields.supplier_account.amounts.dr || 0) -
                  (fields.supplier_account.amounts.cr || 0) +
                  (fields.customer_account.amounts.dr || 0) -
                  (fields.customer_account.amounts.cr || 0), 2)
              }}
            </th>
          </tr>
        </tbody>
      </q-markup-table>
    </q-card>
    <q-card class="q-mt-md q-pa-md">
      <h5 class="q-ma-none">Transactions</h5>
      <div class="row items-center q-mx-sm print-hide">
        <DateRangePicker v-model:startDate="dateRef.start_date" v-model:endDate="dateRef.end_date" :hide-btns="true"
          class="q-mr-md" />
        <span class="row items-end q-gutter-y-sm">
          <q-btn v-if="dateRef.start_date && dateRef.end_date" @click="resetDate" color="red" icon="close"
            class="q-mr-sm"></q-btn>
          <q-btn @click="fetchData" :disable="!(dateRef.start_date && dateRef.end_date)" label="filter"
            color="blue"></q-btn>
        </span>
      </div>
      <TransactionTable v-if="fields.transactions" :fields="fields">
        <TablePagination :fields="fields"></TablePagination>
      </TransactionTable>
    </q-card>
  </div>
</template>

<script lang="ts">
import useApi from 'src/composables/useApi'
import { Ref } from 'vue'
import TransactionTable from 'src/components/account/TransactionTable.vue'
import { useRouter } from 'vue-router'
import { useRoute } from 'vue-router'
export default {
  setup() {
    const metaData = {
      title: 'Party Account | Awecount',
    }
    useMeta(metaData)
    const router = useRouter()
    const route = useRoute()
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
      start_date: string | null,
      end_date: string | null
    }
    const dateRef: Ref<DateRef> = ref({
      start_date: null,
      end_date: null
    })
    function fetchData() {
      if (dateRef.value.start_date && dateRef.value.end_date) {
        router.push(`/parties/account/${route.params.id}/` + `?start_date=${dateRef.value.start_date}&end_date=${dateRef.value.end_date}`)
        const endpoint = `/v1/parties/${route.params.id}/transactions/${`?start_date=${dateRef.value.start_date}&end_date=${dateRef.value.end_date}`}`
        useApi(endpoint, { method: 'GET' })
          .then((data) => {
            fields.value = data
          })
          .catch((error) => {
            if (error.response && error.response.status == 404) {
              router.replace({ path: '/ErrorNotFound' })
            }
          })
      }
    }
    const resetDate = () => {
      dateRef.value = { start_date: null, end_date: null }
      const endpoint = `/v1/parties/${route.params.id}/transactions/`
      router.push(`/parties/account/${route.params.id}/`)
      useApi(endpoint, { method: 'GET' })
        .then((data) => {
          fields.value = data
        })
        .catch((error) => {
          if (error.response && error.response.status == 404) {
            router.replace({ path: '/ErrorNotFound' })
          }
        })
    }
    return {
      fields,
      // journalQueryFilter,
      TransactionTable,
      fetchData,
      dateRef,
      resetDate
    }
  },
  created() {
    const endpoint = `/v1/parties/${this.$route.params.id}/transactions/${this.$route.query.start_date || this.$route.query.end_date ? `?start_date=${this.$route.query.start_date}&end_date=${this.$route.query.end_date}` : ''}`
    if (this.$route.query.start_date && this.$route.query.end_date) {
      this.dateRef = {
        start_date: this.$route.query.start_date,
        end_date: this.$route.query.end_date
      }
    }
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        this.fields = data
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ path: '/ErrorNotFound' })
        }
      })
  },
}
</script>

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