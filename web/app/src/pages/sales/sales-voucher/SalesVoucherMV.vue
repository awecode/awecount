<script lang="ts">
import useApi from 'src/composables/useApi'

export default {
  setup() {
    const metaData = {
      title: 'Sales Invoices Materialized View | Awecount',
    }
    useMeta(metaData)
    interface Fields {
      total_amount: number
    }
    const fields: Ref<Fields | null> = ref(null)
    const onPrintClick = () => {
      window.print()
    }
    const humanizeWord = (word) => {
      word = word.replace(/_/g, ' ')
      return word.charAt(0).toUpperCase() + word.slice(1)
    }
    return {
      fields,
      onPrintClick,
      humanizeWord,
    }
  },
  created() {
    const endpoint = `/api/company/${this.$route.params.company}/sales-voucher/${this.$route.params.id}/details/`
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        const removeArr: Array<string> = ['discount_obj', 'voucher_meta', 'rows', 'enable_row_description', 'payment_receipts', 'can_update_issued', 'issue_datetime', 'available_bank_accounts', 'id', 'options']
        removeArr.forEach(item => delete data[item])
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

<template>
  <div class="q-ma-lg" style="margin-bottom: 100px">
    <q-markup-table>
      <thead>
        <tr class="text-subtitle2 bg-grey-4">
          <th class="text-left">
            Field
          </th>
          <th class="text-left">
            Data
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(value, key) in fields" :key="key">
          <td class="text-left">
            {{ humanizeWord(key) }}
          </td>
          <td class="text-left">
            {{ value }}
          </td>
        </tr>
        <tr class="bg-grey-4 text-subtitle2">
          <td class="text-left">
            Grand Total
          </td>
          <td class="text-left">
            {{ fields?.total_amount }}
          </td>
        </tr>
      </tbody>
    </q-markup-table>
    <q-btn
      class="q-mt-lg"
      icon="print"
      label="Print"
      @click="onPrintClick"
    />
  </div>
</template>
