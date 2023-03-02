<template>
  <div class="q-ma-lg" style="margin-bottom: 100px">
    <q-markup-table>
      <thead>
        <tr class="text-subtitle2 bg-grey-4">
          <th class="text-left">Field</th>
          <th class="text-left">Data</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(value, key) in fields" :key="key">
          <td class="text-left">{{ key }}</td>
          <td class="text-left">{{ value }}</td>
        </tr>
        <tr class="bg-grey-4 text-subtitle2">
          <td class="text-left">Grand Total</td>
          <td class="text-left">{{ fields?.total_amount }}</td>
        </tr>
      </tbody>
    </q-markup-table>
    <q-btn label="Print" icon="print" class="q-mt-lg" />
  </div>
</template>

<script lang="ts">
import useApi from 'src/composables/useApi'
export default {
  setup() {
    const fields = ref(null)
    return {
      fields,
    }
  },
  created() {
    const endpoint = `/v1/sales-voucher/${this.$route.params.id}/details/`
    console.log(endpoint)
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        const removeArr: Array<string> = [
          'discount_obj',
          'voucher_meta',
          'rows',
          'enable_row_description',
          'payment_receipts',
          'can_update_issued',
        ]
        removeArr.forEach((item) => delete data[item])
        this.fields = data
        console.log(this.fields, 'data')
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          this.$router.replace({ name: '404' })
        }
      })
  },
}
// const {
//   columns,
//   rows,
//   resetFilters,
//   filters,
//   loading,
//   searchQuery,
//   pagination,
//   onRequest,
//   confirmDeletion,
//   initiallyLoaded,
// } = useList(endpoint);
</script>
