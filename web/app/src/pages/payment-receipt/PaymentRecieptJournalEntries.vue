<template>
  <JournalVoucherDetails :fields="fields" usedIn="credit_note" />
</template>

<script lang="ts">
import useApi from 'src/composables/useApi'
import JournalVoucherDetails from 'src/components/voucher/JournalVoucherDetails.vue'
import { Ref } from 'vue'

// const getData = () =>
//   useApi(`/v1/journal-voucher/${$this.route.params.id}/`).then((data) => {
//     fields.value = data
//   })
// getData()

export default {
  setup() {
    interface Fields {
      total_amount: number
      voucher_number: number
      status: string
      voucher_no: number
      date: string
      rows: Array<Record<string, number | boolean | string>>
      narration: string
      id: number
    }
    const fields: Ref<Fields | null> = ref(null)
    return {
      fields,
      JournalVoucherDetails,
    }
  },
  created() {
    const endpoint = `/v1/payment-receipt/${this.$route.params.id}/journal-entries/`
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        this.fields = data[0]
        console.log('fields', this.fields)
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) navigateTo('404')
      })
  },
}
</script>
