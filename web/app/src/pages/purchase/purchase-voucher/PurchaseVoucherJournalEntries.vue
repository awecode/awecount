<template>
  <JournalVoucherDetails :fields="fields" usedIn="sales_voucher" />
</template>

<script lang="ts">
import useApi from 'src/composables/useApi'
import JournalVoucherDetails from 'src/components/voucher/JournalVoucherDetails.vue'

// const getData = () =>
//   useApi(`/v1/journal-voucher/${$this.route.params.id}/`).then((data) => {
//     fields.value = data
//   })
// getData()

export default {
  setup() {
    const $q = useQuasar()
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
    const fields: Fields | null = ref(null)
    return {
      fields,
      JournalVoucherDetails,
    }
  },
  created() {
    const router = useRouter()
    const endpoint = `v1/purchase-voucher/${this.$route.params.id}/journal-entries/`
    console.log(endpoint)
    useApi(endpoint, { method: 'GET' })
      .then((data) => {
        this.fields = data[0]
        console.log('fields', this.fields)
      })
      .catch((error) => {
        if (error.response && error.response.status == 404) {
          // router.push('404')
        }
      })
  },
}

// const cancel = (data) => {
//   useApi(`/v1/journal-voucher/${props.id}/cancel/`, {
//     method: 'POST',
//     body: { message: data },
//   })
//     .then(() => {
//       fields.value?.status ? (fields.value.status = 'Cancelled') : ''
//       $q.notify({
//         color: 'positive',
//         message: 'Success',
//         icon: 'check_circle',
//       })
//     })
//     .catch(() => {
//       $q.notify({
//         color: 'negative',
//         message: 'error',
//         icon: 'report_problem',
//       })
//     })
// }

// function prompt() {
//   $q.dialog({
//     title: 'Confirm Cancelation?',
//     message: 'Reason for cancelation?',
//     prompt: {
//       model: '',
//       type: 'text', // optional
//     },
//     cancel: true,
//     persistent: true,
//   })
//     .onOk((data) => {
//       cancel(data)
//     })
//     .onCancel(() => {
//       // console.log('>>>> Cancel')
//     })
//     .onDismiss(() => {
//       // console.log('I am triggered on both OK and Cancel')
//     })
// }
</script>
