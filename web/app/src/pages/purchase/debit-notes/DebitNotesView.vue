<script lang="ts">
import type { Ref } from 'vue'
import DateConverter from 'src/components/date/VikramSamvat.js'
import useGeneratePdf from 'src/composables/pdf/useGeneratePdf'
import useApi from 'src/composables/useApi'
import { modes } from 'src/helpers/constants/invoice'
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
    const route = useRoute()
    useMeta(metaData)
    const store = useLoginStore()
    const $q = useQuasar()
    const fields: Ref<Fields | null> = ref(null)
    const modeOptions: Ref<Array<object> | null> = ref(null)
    const isDeleteOpen: Ref<boolean> = ref(false)
    const deleteMsg: Ref<string> = ref('')
    const isLoading = ref(false)
    const submitChangeStatus = (id: number, status: string) => {
      let endpoint = ''
      let body: null | object = null
      if (status === 'Resolved') {
        endpoint = `/api/company/${route.params.company}/debit-note/${id}/mark_as_resolved/`
        body = { method: 'POST' }
      } else if (status === 'Cancelled') {
        endpoint = `/api/company/${route.params.company}/debit-note/${id}/cancel/`
        body = { method: 'POST', body: { message: deleteMsg.value } }
      }
      isLoading.value = true
      useApi(endpoint, body)
        .then(() => {
          if (fields.value) {
            onStatusChange(status)
          }
          isLoading.value = false
        })
        .catch((err) => {
          isLoading.value = false
          if (err.status === 422) {
            useHandleCancelInconsistencyError(endpoint, err, body.body, $q)
              .then(() => {
                onStatusChange(status)
              })
              .catch((error) => {
                if (error.status !== 'cancel') {
                  $q.notify({
                    color: 'negative',
                    message:
                      'Server Error! Please contact us with the problem.',
                    icon: 'report_problem',
                  })
                }
              })
          } else {
            let message = null
            message = err?.data?.detail
            $q.notify({
              color: 'red-6',
              message:
                message || 'Server Error! Please contact us with the problem.',
            })
            isLoading.value = false
          }
        })
    }
    const getDate = computed(() => {
      return DateConverter.getRepresentation(
        fields.value?.date,
        store.isCalendarInAD ? 'ad' : 'bs',
      )
    })
    const print = (bodyOnly: boolean) => {
      const printData = useGeneratePdf('debitNote', bodyOnly, fields.value)
      usePrintPdfWindow(printData)
    }
    const onPrintclick = (noApiCall) => {
      if (!noApiCall) {
        const endpoint = `/api/company/${route.params.company}/debit-note/${fields.value?.id}/log-print/`
        useApi(endpoint, { method: 'POST' })
          .then(() => {
            if (fields.value) {
              print(false)
              fields.value.print_count = fields.value?.print_count + 1
            }
          })
          .catch(err => console.log('err from the api', err))
      } else {
        print(false)
      }
    }
    const discountComputed = computed(() => {
      if (fields.value?.discount_obj) {
        return (
          `${fields.value.discount_obj.value}`
          + ' '
          + `${fields.value.discount_obj.type === 'Amount' ? '-/' : '%'}`
        )
      } else if (fields.value?.discount) {
        return (
          `${fields.value.discount}`
          + ' '
          + `${fields.value.discount_type === 'Amount' ? '-/' : '%'}`
        )
      } else {
        return false
      }
    })
    const onStatusChange = (status) => {
      fields.value.status = status
      if (status === 'Cancelled') {
        $q.notify({
          color: 'green-6',
          message: 'Voucher has been cancelled.',
        })
        isDeleteOpen.value = false
      } else if (status === 'Resolved') {
        $q.notify({
          color: 'green-6',
          message: 'Voucher Marked as Resolved.',
        })
      }
    }
    return {
      allowPrint: false,
      bodyOnly: false,
      options: {},
      fields,
      dialog: false,
      partyObj: null,
      modes,
      submitChangeStatus,
      modeOptions,
      discountComputed,
      isDeleteOpen,
      deleteMsg,
      onPrintclick,
      getDate,
      checkPermissions,
      isLoading,
    }
  },
  created() {
    const endpoint = `/api/company/${this.$route.params.company}/debit-note/${this.$route.params.id}/details/`
    useApi(endpoint, { method: 'GET' }, false, true)
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

<template>
  <div v-if="fields" class="sales-invoice">
    <q-card class="q-ma-lg q-mb-sm">
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Debit Note | {{ fields?.status }} | #{{ fields?.voucher_no }}</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pa-lg row text-grey-8 text-body2 row" style="padding-bottom: 0">
        <div class="col-12 col-md-6 column q-gutter-y-lg q-mb-lg">
          <div class="row">
            <div class="col-6">
              Party
            </div>
            <div class="col-6">
              {{ fields?.party_name }}
            </div>
          </div>
          <div class="row">
            <div class="col-6">
              Address
            </div>
            <div class="col-6">
              {{ fields?.address }}
            </div>
          </div>
          <div class="row">
            <div class="col-6">
              Status
            </div>
            <div class="col-6">
              {{ fields?.status }}
            </div>
          </div>
          <div v-if="discountComputed" class="row">
            <div class="col-6">
              Discount
            </div>
            <div class="col-6">
              {{ discountComputed }}
            </div>
          </div>
        </div>
        <div class="col-12 col-md-6 column q-gutter-y-lg q-mb-lg">
          <div class="row">
            <div class="col-6">
              Date
            </div>
            <div class="col-6" style="height: 20px">
              {{ getDate }}
            </div>
          </div>
          <div class="row">
            <div class="col-6">
              Payment Mode
            </div>
            <div class="col-6">
              {{ fields?.payment_mode ?? 'Credit' }}
            </div>
          </div>
        </div>
      </q-card>
    </q-card>
    <div class="q-ma-lg text-subtitle2">
      Ref. Invoice No.: #
      {{ fields?.invoice_data && fields?.invoice_data[0]?.voucher_no }}
    </div>
    <q-card id="to_print" class="q-mx-lg">
      <q-card-section>
        <ViewerTable :fields="fields" />
      </q-card-section>
    </q-card>
    <q-card v-if="fields?.remarks" class="q-mx-lg q-my-md">
      <q-card-section>
        <span class="text-subtitle2 text-grey-9"> Remarks: </span>
        <span class="text-grey-9">{{ fields?.remarks }}</span>
      </q-card-section>
    </q-card>
    <div v-if="fields" class="q-px-lg q-pb-lg q-mt-md row justify-between q-gutter-x-md d-print-none">
      <div class="row">
        <div v-if="fields?.status !== 'Cancelled'" class="row q-gutter-x-md q-gutter-y-md q-mb-md">
          <q-btn
            v-if="checkPermissions('DebitNoteModify')
              && (fields.can_update_issued || fields.status === 'Draft')
            "
            :to="`/${$route.params.company}/debit-note/${fields.id}`"
            color="orange-6"
            label="Edit"
            icon="edit"
          />
          <q-btn
            v-if="fields?.status === 'Issued' && checkPermissions('DebitNoteModify')
            "
            :loading="isLoading"
            color="green-6"
            label="mark as resolved"
            icon="mdi-check-all"
            @click.prevent="() => submitChangeStatus(fields?.id, 'Resolved')"
          />
          <q-btn
            v-if="checkPermissions('DebitNoteCancel')"
            :loading="isLoading"
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
          :label="`Print ${fields.print_count > 0 ? `Copy No. ${fields.print_count}` : ''
          }`"
          icon="print"
          @click="onPrintclick(false)"
        />
        <q-btn v-else label="Print" icon="print" @click="onPrintclick(true)" />
        <q-btn
          v-if="fields?.status === 'Issued' || fields?.status === 'Resolved'"
          color="blue-7"
          label="Journal Entries"
          icon="books"
          :to="`/${$route.params.company}/journal-entries/debit-note/${fields?.id}/`"
        />
      </div>
    </div>
    <!-- <q-dialog v-model="isDeleteOpen">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-red-6">
          <div class="text-h6 text-white">
            <span>Confirm Cancelation?</span>
          </div>
        </q-card-section>

        <q-card-section class="q-ma-md">
          <q-input v-model="deleteMsg" type="textarea" outlined> </q-input>
          <div class="text-right q-mt-lg">
            <q-btn label="Confirm" @click="() => submitChangeStatus(fields?.id, 'Cancelled')"></q-btn>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog> -->
    <q-dialog v-model="isDeleteOpen">
      <q-card style="min-width: min(40vw, 400px)">
        <q-card-section class="bg-red-6 q-py-md flex justify-between">
          <div class="text-h6 text-white">
            <span>Confirm Cancellation?</span>
          </div>
          <q-btn v-close-popup icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense />
        </q-card-section>
        <q-separator inset />
        <q-card-section>
          <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500">
            Are you sure?
          </div>
          <div class="text-blue">
            <div class="row justify-end">
              <q-btn flat class="q-mr-md text-blue-grey-9" label="NO" @click="() => (isDeleteOpen = false)" />
              <q-btn flat class="text-red" label="Yes" @click="() => submitChangeStatus(fields?.id, 'Cancelled')" />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped>
@media print {

  /* @import url("https://fonts.googleapis.com/css?family=Arbutus+Slab&display=swap"); */
  .q-card {
    box-shadow: none;
    padding: 0;
  }
}
</style>
