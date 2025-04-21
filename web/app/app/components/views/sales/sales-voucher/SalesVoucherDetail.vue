<script lang="ts">
import type { Ref } from 'vue'
import useGeneratePdf from '@/composables/pdf/useGeneratePdf'
import { modes } from '@/helpers/constants/invoice'
import { useLoginStore } from '@/stores/login-info'
import { parseErrors } from '@/utils/helpers'

interface Fields {
  status: string
  voucher_no: string
  remarks: string
  print_count: number
  id: number
  payment_mode: number
  options: {
    show_rate_quantity_in_voucher: boolean
    default_email_attachments: File[]
  }
  email: string
  party_email: string
  customer_name: string
  party_name: string
  hash: string
  company: any
}
export default {
  setup() {
    const metaData = {
      title: 'Sales Invoices | Awecount',
    }
    const route = useRoute()
    useHead(metaData)
    const $q = useQuasar()
    const fields: Ref<Fields | null> = ref(null)
    const loading: Ref<boolean> = ref(false)
    const paymentModeOptions: Ref<Array<object> | null> = ref(null)
    const isDeleteOpen: Ref<boolean> = ref(false)
    const deleteMsg: Ref<string> = ref('')
    const errors = ref({})
    const isLoggedIn = useLoginStore().isLoggedIn
    const emailInvoiceErrors = ref<Record<string, string>>({})
    const isEmailInvoiceModalOpen: Ref<boolean> = ref(false)
    const loginStore = useLoginStore()

    const emailInvoicePayload = ref({
      attach_pdf: true,
      attachments: [],
      to: '',
      subject: '',
      message: '',
    })

    function resetEmailInvoicePayload() {
      emailInvoiceErrors.value = {}
      emailInvoicePayload.value = {
        attach_pdf: true,
        attachments: fields.value?.options?.default_email_attachments || [],
        to: [fields.value.email, fields.value.party_email].filter(Boolean),
        subject: `Sales Invoice #${fields.value.voucher_no}`,
        message: `
          <p>Hello <b>${fields.value.customer_name || fields.value.party_name}</b>,</p>
          <p>I hope this message finds you well.</p>
          <p>Please find attached the invoice <b>#${fields.value?.voucher_no}</b></p>
          <p>You can view and download the invoice using the following link: <a href="${`${window.location.protocol}//${window.location.host}${window.location.pathname}`}?hash=${fields.value?.hash}">View Invoice</a>.</p>
          <p>If you have any questions or require further assistance, feel free to contact us at <b>${loginStore.companyInfo?.contact_no || '[]'}</b>.</p>
          <p>Best Regards,<br>
          <b>${loginStore.companyInfo?.name || '[]'}</b></p>
        `,
      }
    }

    function emailInvoice() {
      const endpoint = `api/company/${route.params.company}/sales-voucher/${fields.value?.id}/email-invoice/`
      const formData = new FormData()
      formData.append('attach_pdf', emailInvoicePayload.value.attach_pdf ? 'true' : 'false')
      emailInvoicePayload.value.attachments.forEach((file: File) => {
        formData.append('attachments', file)
      })
      emailInvoicePayload.value.to.forEach((email: string) => {
        formData.append('to', email)
      })
      formData.append('subject', emailInvoicePayload.value.subject)
      formData.append('message', emailInvoicePayload.value.message)
      useApi(endpoint, {
        body: formData,
        method: 'POST',
      })
        .then(() => {
          isEmailInvoiceModalOpen.value = false
          if (isLoggedIn) resetEmailInvoicePayload()
          $q.notify({
            color: 'positive',
            message: 'Invoice Sent!',
            icon: 'check_circle',
          })
        })
        .catch((err) => {
          if (err.response.status === 400) {
            emailInvoiceErrors.value = parseErrors(err.data)
          }
        })
    }

    const print = (bodyOnly: boolean) => {
      const printData = useGeneratePdf('salesVoucher', bodyOnly, fields.value, !fields.value.options.show_rate_quantity_in_voucher, isLoggedIn ? null : fields.value.company)
      usePrintPdfWindow(printData)
    }

    const submitChangeStatus = (id: number, status: string) => {
      loading.value = true
      let endpoint = ''
      let body: null | object = null
      if (status === 'Paid') {
        endpoint = `/api/company/${route.params.company}/sales-voucher/${id}/mark_as_paid/`
        body = { method: 'POST' }
      } else if (status === 'Cancelled') {
        endpoint = `/api/company/${route.params.company}/sales-voucher/${id}/cancel/`
        body = { method: 'POST', body: { message: deleteMsg.value } }
      }
      useApi(endpoint, body)
        .then(() => {
          if (fields.value) {
            fields.value.status = status
          }
          if (status === 'Cancelled') {
            isDeleteOpen.value = false
            fields.value.remarks = `\nReason for cancellation: ${body?.body.message}`
          }
          loading.value = false
        })
        .catch((data) => {
          if (data.status === 422) {
            useHandleCancelInconsistencyError(endpoint, data, body.body, $q)
              .then(() => {
                if (fields.value) {
                  fields.value.status = status
                }
                if (status === 'Cancelled') {
                  isDeleteOpen.value = false
                  fields.value.remarks = `\nReason for cancellation: ${body?.body.message}`
                }
                loading.value = false
              })
              .catch((error) => {
                if (error.status !== 'cancel') {
                  $q.notify({
                    color: 'negative',
                    message: 'Something went Wrong!',
                    icon: 'report_problem',
                  })
                }
                loading.value = false
              })
          } else {
            const parsedError = useHandleFormError(data)
            errors.value = parsedError.errors
            $q.notify({
              color: 'negative',
              message: parsedError.message,
              icon: 'report_problem',
            })
            loading.value = false
          }
        })
    }
    const updatePaymentMode = (newValue: number) => {
      if (fields.value) {
        fields.value.payment_mode = newValue
      }
    }

    const onPrintclick = (bodyOnly: boolean, noApiCall = false) => {
      if (!noApiCall) {
        const endpoint = `/api/company/${route.params.company}/sales-voucher/${fields.value.id}/log-print/`
        useApi(endpoint, { method: 'POST' })
          .then(() => {
            if (fields.value) {
              fields.value.print_count = fields.value?.print_count + 1
            }
            print(bodyOnly)
          })
          .catch(err => console.log('err from the api', err))
      } else {
        print(bodyOnly)
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
      isDeleteOpen,
      deleteMsg,
      updatePaymentMode,
      paymentModeOptions,
      onPrintclick,
      checkPermissions,
      useGeneratePdf,
      loading,
      errors,
      isLoggedIn,
      isEmailInvoiceModalOpen,
      emailInvoicePayload,
      emailInvoice,
      resetEmailInvoicePayload,
      emailInvoiceErrors,
    }
  },
  created() {
    let endpoint = `/api/company/${this.$route.params.company}/sales-voucher/${this.$route.params.id}/details/`
    if (!this.isLoggedIn && this.$route.query.hash) {
      endpoint = `/api/company/${this.$route.params.company}/sales-voucher/${this.$route.params.id}/details-by-hash/?hash=${this.$route.query.hash}`
    }
    useApi(endpoint, { method: 'GET' }, false, true)
      .then((data) => {
        this.fields = data
        this.paymentModeOptions = data.available_payment_modes
        this.resetEmailInvoicePayload()
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
    <div class="d-print-none">
      <q-card class="q-ma-lg q-mb-sm">
        <q-card-section class="bg-green text-white">
          <div class="text-h6 d-print-none">
            <span>
              Sales Invoice | {{ fields?.status }}
              <span v-if="fields?.voucher_no">| # {{ fields?.voucher_no }}</span>
            </span>
          </div>
        </q-card-section>
        <ViewerHeader2
          :change-modes="isLoggedIn"
          :fields="fields"
          :payment-mode-options="paymentModeOptions"
          @update-mode="(newValue) => updatePaymentMode(newValue)"
        />
      </q-card>
      <q-card id="to_print" class="q-mx-lg">
        <q-card-section>
          <ViewerTable :fields="fields" :show-rate-quantity="fields.options.show_rate_quantity_in_voucher" />
        </q-card-section>
      </q-card>
      <div v-if="fields?.payment_receipts && fields?.payment_receipts.length > 0">
        <q-card
          v-for="receipt in fields.payment_receipts"
          id="to_print"
          :key="receipt"
          class="q-mx-lg q-mt-md"
        >
          <q-card-section>
            <div class="row">
              <div class="col-3">
                Receipt #
                <router-link
                  v-if="checkPermissions('paymentreceipt.read')"
                  class="text-blue"
                  style="font-weight: 500; text-decoration: none"
                  :to="`/${$route.params.company}/payment-receipts/${receipt.id}`"
                >
                  {{ receipt.id }}
                </router-link>
              </div>
              <div class="col-3">
                Amount:
                <FormattedNumber type="currency" :value="receipt.amount" />
              </div>
              <div class="col-3">
                Status:
                <span class="text-weight-medium">{{ receipt.status }}</span>
              </div>
              <div class="col-3">
                TDS Amount:
                <FormattedNumber type="currency" :value="receipt.tds_amount" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
      <q-card v-if="fields?.remarks" class="q-mx-lg q-my-md">
        <q-card-section>
          <span class="text-subtitle2 text-grey-9">Remarks:</span>
          <span class="text-grey-9">{{ fields?.remarks }}</span>
        </q-card-section>
      </q-card>
      <div v-if="fields" class="q-px-lg q-pb-lg q-mt-md row justify-between q-gutter-x-md d-print-none">
        <div>
          <div class="row q-gutter-x-md q-gutter-y-md q-mb-md">
            <q-btn
              v-if="checkPermissions('sales.update') && (fields.can_update_issued || fields?.status === 'Draft')"
              color="orange-5"
              icon="edit"
              label="Edit"
              :to="`/${$route.params.company}/sales/vouchers/${fields?.id}/edit`"
            />
            <q-btn
              v-if="fields?.status === 'Issued' && checkPermissions('sales.update')"
              color="green-6"
              icon="mdi-check-all"
              label="mark as paid"
              :loading="loading"
              @click.prevent="() => submitChangeStatus(fields?.id, 'Paid')"
            />
            <q-btn
              v-if="checkPermissions('sales.cancel') && fields?.status !== 'Cancelled'"
              color="red-5"
              icon="cancel"
              label="Cancel"
              :loading="loading"
              @click.prevent="() => (isDeleteOpen = true)"
            />
          </div>
        </div>
        <div class="row q-gutter-x-md q-gutter-y-md q-mb-md justify-end">
          <q-btn icon="print" :label="`Print ${fields?.print_count ? `Copy ${['Draft', 'Cancelled'].includes(fields?.status) ? '' : `# ${fields?.print_count || 0}`}` : ''}`" @click="() => onPrintclick(false, fields?.status === 'Draft')" />
          <q-btn icon="print" :label="`Print Body ${['Draft', 'Cancelled'].includes(fields?.status) ? '' : `# ${(fields?.print_count || 0) + 1}`}`" @click="() => onPrintclick(true, fields?.status === 'Draft')" />
          <q-btn
            v-if="isLoggedIn && !['Draft', 'Cancelled'].includes(fields?.status)"
            data-testid="send-email"
            label="Send email"
            @click="isEmailInvoiceModalOpen = true"
          />
          <q-btn
            color="blue-7"
            icon="mdi-table"
            label="Materialized View"
            :to="`/${$route.params.company}/sales/vouchers/${fields?.id}/materialized-view`"
          />
          <q-btn
            v-if="fields?.status !== 'Cancelled' && fields?.status !== 'Draft'"
            color="blue-7"
            icon="books"
            label="Journal Entries"
            :to="`/${$route.params.company}/journal-entries/sales-voucher/${fields.id}`"
          />
        </div>
        <q-dialog v-model="isDeleteOpen" class="overflow-visible" @before-hide="errors = {}">
          <q-card class="overflow-visible" style="min-width: min(40vw, 500px)">
            <q-card-section class="bg-red-6 flex justify-between">
              <div class="text-h6 text-white">
                <span>Confirm Cancellation?</span>
              </div>
              <q-btn
                v-close-popup
                dense
                flat
                round
                class="text-red-700 bg-slate-200 opacity-95"
                icon="close"
              />
            </q-card-section>

            <q-card-section class="q-ma-md">
              <q-input
                v-model="deleteMsg"
                autofocus
                outlined
                type="textarea"
                :error="!!errors?.message"
                :error-message="errors?.message"
              />
              <div class="text-right q-mt-lg">
                <q-btn label="Confirm" @click="() => submitChangeStatus(fields?.id, 'Cancelled')" />
              </div>
            </q-card-section>
          </q-card>
        </q-dialog>
      </div>
    </div>

    <q-dialog v-model="isEmailInvoiceModalOpen" @hide="resetEmailInvoicePayload">
      <q-card style="min-width: min(60vw, 800px)">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6 flex justify-between">
            <span class="q-mx-md">Send invoice in email</span>
            <q-btn
              v-close-popup
              dense
              flat
              round
              class="text-white bg-red-500"
              icon="close"
            />
          </div>
        </q-card-section>
        <q-card-section class="q-mx-md flex flex-col gap-4">
          <q-select
            v-model="emailInvoicePayload.to"
            filled
            hide-dropdown-icon
            multiple
            use-chips
            use-input
            input-debounce="0"
            label="To"
            new-value-mode="add-unique"
            :error="!!emailInvoiceErrors.to"
            :error-message="typeof emailInvoiceErrors.to === 'string' ? emailInvoiceErrors.to : 'Enter valid email address'"
          />
          <q-input
            v-model="emailInvoicePayload.subject"
            outlined
            label="Subject"
            :error="!!emailInvoiceErrors.subject"
            :error-message="emailInvoiceErrors.subject"
          />
          <q-editor v-model="emailInvoicePayload.message" />
          <q-checkbox v-model="emailInvoicePayload.attach_pdf" label="Attach PDF" />
          <file-uploader
            v-model="emailInvoicePayload.attachments"
            multiple
            label="Attachments"
            :error="emailInvoiceErrors.attachments"
          />
          <div class="row justify-end">
            <q-btn
              class="q-mt-md"
              color="orange-5"
              label="Send"
              @click="emailInvoice"
            />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<style scoped lang="scss">
@media print {
  @import url('https://fonts.googleapis.com/css?family=Arbutus+Slab&display=swap');

  .d-print-none {
    display: none;
    visibility: hidden;
    width: none;
  }
}
</style>
