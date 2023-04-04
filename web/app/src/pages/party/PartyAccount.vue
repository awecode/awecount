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
          <tr
            v-if="
              fields.supplier_account &&
              (fields.supplier_account.amounts.dr != null ||
                fields.supplier_account.amounts.cr != null)
            "
          >
            <td class="text-left">
              <router-link
                :to="`/account/${fields.supplier_account?.id}/view/`"
                class="text-blue"
                style="text-decoration: none"
              >
                Vendor (Payable)
              </router-link>
            </td>
            <td class="text-left">{{ fields.supplier_account.code }}</td>
            <td class="text-left">
              {{ fields.supplier_account.amounts.dr || '' }}
            </td>
            <td class="text-left">
              {{ fields.supplier_account.amounts.cr || '' }}
            </td>
            <td class="text-left">
              {{
                (fields.supplier_account.amounts.dr || 0) -
                (fields.supplier_account.amounts.cr || 0)
              }}
            </td>
          </tr>
          <tr
            v-if="
              fields.customer_account &&
              (fields.customer_account.amounts.dr != null ||
                fields.customer_account.amounts.cr != null)
            "
          >
            <td class="text-left">
              <router-link
                :to="`/account/${fields.customer_account?.id}/view/`"
                class="text-blue"
                style="text-decoration: none"
              >
                Customer (Receivable)
              </router-link>
            </td>
            <td class="text-left">{{ fields.customer_account.code }}</td>
            <td class="text-left">
              {{ fields.customer_account.amounts.dr || '' }}
            </td>
            <td class="text-left">
              {{ fields.customer_account.amounts.cr || '' }}
            </td>
            <td class="text-left">
              {{
                (fields.customer_account.amounts.dr || 0) -
                (fields.customer_account.amounts.cr || 0)
              }}
            </td>
          </tr>
          <tr v-if="fields.supplier_account && fields.customer_account">
            <td colspan="2"></td>
            <th class="text-left">
              {{
                fields.supplier_account.amounts.dr ||
                0 + fields.customer_account.amounts.dr ||
                0
              }}
            </th>
            <th class="text-left">
              {{
                fields.supplier_account.amounts.cr ||
                0 + fields.customer_account.amounts.cr ||
                0
              }}
            </th>
            <th class="text-left">
              {{
                (fields.supplier_account.amounts.dr || 0) -
                (fields.supplier_account.amounts.cr || 0) +
                (fields.customer_account.amounts.dr || 0) -
                (fields.customer_account.amounts.cr || 0)
              }}
            </th>
          </tr>
        </tbody>
      </q-markup-table>
    </q-card>
    <q-card class="q-mt-md q-pa-md">
      <h5 class="q-ma-none">Transactions</h5>
      <div class="q-mt-sm row items-end q-gutter-x-md q-gutter-y-sm">
        <q-input label="Start Date"></q-input>
        <q-input label="End Date"></q-input>
        <span class="row items-end q-gutter-y-sm">
          <q-btn color="red" icon="close" class="q-mr-sm"></q-btn>
          <q-btn label="filter" color="blue"></q-btn>
        </span>
      </div>
      <TransactionTable v-if="fields.transactions" :fields="fields" />
    </q-card>
  </div>
</template>

<script lang="ts">
import useApi from 'src/composables/useApi'
import { Ref } from 'vue'
import TransactionTable from 'src/components/account/TransactionTable.vue'
export default {
  setup() {
    const metaData = {
      title: 'Party Account | Awecount',
    }
    useMeta(metaData)
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
    function journalQueryFilter() {
      const { start_date, end_date } = this.filters
      if (!(start_date && end_date)) {
        this.$error('Date Range not set.')
        return
      }
      const start_date_object = new Date(start_date)
      const end_date_object = new Date(end_date)
      if (start_date_object > end_date_object) {
        this.$error('Start Date greater than end date')
        return
      }
      const queryParam = { start_date: start_date, end_date: end_date }
      this.$router.replace({ query: queryParam }).catch(() => {
        console.log('err')
      })

      this.$http
        .get(this.getEndPoint(), {
          params: this.filters,
        })
        .then(({ data }) => {
          this.fields = Object.assign({}, this.fields, data)
        })
    }
    // function getEndPoint() {
    //   return `parties/${this.$route.params.pk}/transactions/`
    // }
    return {
      fields,
      journalQueryFilter,
      TransactionTable,
    }
  },
  created() {
    const endpoint = `/v1/parties/${this.$route.params.id}/transactions/`
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        this.fields = data
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ name: '404' })
        }
      })
  },
}
</script>
