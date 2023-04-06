<template>
  <div v-if="fields" class="sales-invoice">
    <q-card class="q-ma-lg q-mb-sm">
      <q-card-section class="bg-green text-white">
        <div class="text-h6 d-print-none">
          <span
            >Debit Note | {{ fields?.status }} | #{{ fields?.voucher_no }}</span
          >
        </div>
      </q-card-section>

      <q-card
        class="q-mx-lg q-pa-lg row text-grey-8 text-body2 row"
        style="padding-bottom: 0"
      >
        <div class="col-12 col-md-6 column q-gutter-y-lg q-mb-lg">
          <div class="row">
            <div class="col-6">Party</div>
            <div class="col-6">{{ fields?.party_name }}</div>
          </div>
          <div class="row">
            <div class="col-6">Address</div>
            <div class="col-6">{{ fields?.address }}</div>
          </div>
          <div class="row">
            <div class="col-6">Status</div>
            <div class="col-6">{{ fields?.status }}</div>
          </div>
          <div class="row" v-if="discountComputed">
            <div class="col-6">Discount</div>
            <div class="col-6">{{ discountComputed }}</div>
          </div>
        </div>
        <div class="col-12 col-md-6 column q-gutter-y-lg q-mb-lg">
          <div class="row">
            <div class="col-6">Date</div>
            <div class="col-6" style="height: 20px">
              {{ getDate }}
            </div>
          </div>
          <div class="row">
            <div class="col-6">Mode</div>
            <div class="col-6">{{ fields?.mode }}</div>
          </div>
        </div>
      </q-card>
    </q-card>
    <q-card class="q-mx-lg" id="to_print">
      <q-card-section>
        <ViewerTable :fields="fields" />
      </q-card-section>
    </q-card>
    <q-card class="q-mx-lg q-my-md" v-if="fields?.remarks">
      <q-card-section>
        <span class="text-subtitle2 text-grey-9"> Remarks: </span>
        <span class="text-grey-9">{{ fields?.remarks }}</span>
      </q-card-section>
    </q-card>
    <div
      class="q-px-lg q-pb-lg q-mt-md row justify-between q-gutter-x-md d-print-none"
      v-if="fields"
    >
      <div class="row">
        <div
          v-if="fields?.status !== 'Cancelled'"
          class="row q-gutter-x-md q-gutter-y-md q-mb-md"
        >
          <q-btn
            v-if="fields?.status === 'Issued'"
            @click.prevent="() => submitChangeStatus(fields?.id, 'Paid')"
            color="green-6"
            label="mark as paid"
            icon="mdi-check-all"
          />
          <q-btn
            color="red-5"
            label="Cancel"
            icon="cancel"
            @click.prevent="() => (isDeleteOpen = true)"
          />
        </div>
      </div>
      <div class="row q-mb-md q-gutter-x-md">
        <q-btn
          v-if="fields?.status !== 'Cancelled' && fields?.status !== 'Draft'"
          :label="`Print Copy No. ${fields.print_count}`"
          icon="print"
          @click="onPrintclick"
        />
        <q-btn v-else label="Print" icon="print" @click="onPrintclick" />
        <q-btn
          v-if="fields?.status === 'Issued' || fields?.status === 'Paid'"
          color="blue-7"
          label="Journal Entries"
          icon="books"
          :to="`/journal-entries/debit-note/${fields?.id}/`"
        />
      </div>
    </div>
    <q-dialog v-model="isDeleteOpen">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-red-6">
          <div class="text-h6 text-white">
            <span>Confirm Cancelation?</span>
          </div>
        </q-card-section>

        <q-card-section class="q-ma-md">
          <q-input v-model="deleteMsg" type="textarea" outlined> </q-input>
          <div class="text-right q-mt-lg">
            <q-btn
              label="Confirm"
              @click="() => submitChangeStatus(fields?.id, 'Cancelled')"
            ></q-btn>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script lang="ts">
import useApi from 'src/composables/useApi'
import { modes } from 'src/helpers/constants/invoice'
import { Ref } from 'vue'
import useGeneratePdf from 'src/composables/pdf/useGeneratePdf'
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
interface Fields {
  status: string
  voucher_no: string
  remarks: string
  print_count: number
  id: number
  mode: number
  party_name: string
  date: string
  discount_obj: null | Record<string, string | number>
  discount: null | number
  discount_type: null | 'Amount' | 'Percent'
  address: string
}
export default {
  setup() {
    const metaData = {
      title: 'Debit Note | Awecount',
    }
    useMeta(metaData)
    const store = useLoginStore()
    const $q = useQuasar()
    const fields: Ref<Fields | null> = ref(null)
    const modeOptions: Ref<Array<object> | null> = ref(null)
    const isDeleteOpen: Ref<boolean> = ref(false)
    const deleteMsg: Ref<string> = ref('')
    const submitChangeStatus = (id: number, status: string) => {
      let endpoint = ''
      let body: null | object = null
      if (status === 'Paid') {
        endpoint = `/v1/purchase-vouchers/${id}/mark_as_paid/`
        body = { method: 'POST' }
      } else if (status === 'Cancelled') {
        endpoint = `/v1/purchase-vouchers/${id}/cancel/`
        body = { method: 'POST', body: { message: deleteMsg.value } }
      }
      useApi(endpoint, body)
        .then(() => {
          // if (fields.value)
          if (fields.value) {
            fields.value.status = status
            if (status === 'Cancelled') {
              $q.notify({
                color: 'green-6',
                message: 'Voucher has been cancelled.',
              })
              isDeleteOpen.value = false
            } else if (status === 'Paid') {
              $q.notify({
                color: 'green-6',
                message: 'Voucher Marked as paid.',
              })
            }
          }
        })
        .catch(() => {
          // TODO: Properly Parse Error and show
          $q.notify({
            color: 'red-6',
            message: 'Something Went Wrong!',
          })
        })
    }
    const getDate = computed(() => {
      return DateConverter.getRepresentation(
        fields.value?.date,
        store.isCalendarInAD ? 'ad' : 'bs'
      )
    })
    const print = (bodyOnly) => {
      let ifram = document.createElement('iframe')
      ifram.style = 'display:none; margin: 20px'
      document.body.appendChild(ifram)
      const pri = ifram.contentWindow
      pri.document.open()
      pri.document.write(useGeneratePdf('debitNote', bodyOnly, fields.value))
      // pri.document.body.firstElementChild.prepend()
      pri.document.close()
      pri.focus()
      setTimeout(() => pri.print(), 100)
    }
    const onPrintclick = () => {
      const endpoint = `/v1/debit-note/${fields.value?.voucher_no}/log-print/`
      useApi(endpoint, { method: 'POST' })
        .then(() => {
          if (fields.value) {
            print(false)
            fields.value.print_count = fields.value?.print_count + 1
          }
        })
        .catch((err) => console.log('err from the api', err))
    }
    const discountComputed = computed(() => {
      if (fields.value?.discount_obj) {
        return (
          `${fields.value.discount_obj.value}` +
          ' ' +
          `${fields.value.discount_obj.type === 'Amount' ? '-/' : '%'}`
        )
      } else if (fields.value?.discount) {
        return (
          `${fields.value.discount}` +
          ' ' +
          `${fields.value.discount_type === 'Amount' ? '-/' : '%'}`
        )
      } else return false
    })
    return {
      allowPrint: false,
      bodyOnly: false,
      options: {},
      fields,
      dialog: false,
      partyObj: null,
      modes: modes,
      submitChangeStatus,
      modeOptions,
      discountComputed,
      isDeleteOpen,
      deleteMsg,
      onPrintclick,
      getDate,
    }
  },
  created() {
    const endpoint = `/v1/debit-note/${this.$route.params.id}/details/`
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
