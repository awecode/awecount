<script setup lang="ts">
import { useMeta } from 'quasar'
import checkPermissions from 'src/composables/checkPermissions'
import useApi from 'src/composables/useApi'
import { useLoginStore } from 'src/stores/login-info'
import { parseErrors } from 'src/utils/helpers'
import { generateQuotationPDF } from 'src/utils/pdf'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

interface Fields {
  status: string
  number: string
  remarks: string
  id: number
  email: string
  sales_invoice_id: number | null
  party_email: string
  customer_name: string
  party_name: string
  hash: string
  company: any
}

const metaData = {
  title: 'Quotation | Awecount',
}
useMeta(metaData)

const route = useRoute()
const router = useRouter()
const $q = useQuasar()
const fields = ref<Fields | null>(null)
const paymentModeOptions = ref<Array<object> | null>(null)
const isLoggedIn = useLoginStore().isLoggedIn
const emailInvoiceErrors = ref<Record<string, string>>({})
const isEmailInvoiceModalOpen = ref(false)
const loginStore = useLoginStore()

const triggerPrint = route.query.print === 'true'

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
    attachments: [],
    to: [fields.value?.email, fields.value?.party_email].filter(Boolean),
    subject: `Quotation #${fields.value?.number}`,
    message: `
      <p>Hello <b>${fields.value?.customer_name || fields.value?.party_name}</b>,</p>
      <p>I hope this message finds you well.</p>
      <p>Please find attached the quotation <b>#${fields.value?.number}</b></p>
      <p>You can view and download the quotation using the following link: <a href="${`${window.location.protocol}//${window.location.host}${window.location.pathname}`}?hash=${fields.value?.hash}">View Quotation</a>.</p>
      <p>If you have any questions or require further assistance, feel free to contact us at <b>${loginStore.companyInfo?.contact_no || '[]'}</b>.</p>
      <p>Best Regards,<br>
      <b>${loginStore.companyInfo?.name || '[]'}</b></p>
    `,
  }
}

function emailInvoice() {
  const endpoint = `api/company/${route.params.company}/quotation/${fields.value?.id}/email/`
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
  const printData = generateQuotationPDF(bodyOnly, fields.value, isLoggedIn ? null : fields.value.company)
  usePrintPdfWindow(printData)
}

const endpoint = `/api/company/${route.params.company}/quotation/${route.params.id}/details/`
useApi(endpoint, { method: 'GET' }, false, true)
  .then((data) => {
    fields.value = data
    fields.value.voucher_meta = fields.value.quotation_meta
    resetEmailInvoicePayload()
    if (triggerPrint) {
      print(false)
    }
  })
  .catch((error) => {
    if (error.response && error.response.status === 404) {
      router.replace({ path: '/ErrorNotFound' })
    }
  })

const isConvertModalOpen = ref(false)
const convertToInvoice = () => {
  const endpoint = `/api/company/${route.params.company}/quotation/${fields.value?.id}/convert/`
  useApi(endpoint, { method: 'POST' }, false, true)
    .then((res) => {
      isConvertModalOpen.value = false
      router.push({ path: `/${route.params.company}/sales/vouchers/${res?.id}` })
    })
    .catch((error) => {
      if (error.response && error.response.status === 404) {
        router.replace({ path: '/ErrorNotFound' })
      }
    })
}
</script>

<template>
  <div v-if="fields" class="quotation">
    <div class="d-print-none">
      <q-card class="q-ma-lg q-mb-sm">
        <q-card-section class="bg-green text-white">
          <div class="text-h6 d-print-none">
            <span>
              Quotation | {{ fields?.status }}
              <span v-if="fields?.number">| # {{ fields?.number }}</span>
            </span>
          </div>
        </q-card-section>
        <q-card class="q-mx-lg q-pa-lg row text-grey-8 text-body2">
          <div class="col-12 col-md-6 q-gutter-y-lg q-mb-lg">
            <template v-if="fields?.party_name">
              <div class="col-12 col-md-6 row">
                <div class="col-6">
                  Party
                </div>
                <div class="col-6">
                  {{ fields?.party_name }}
                </div>
              </div>
              <div v-if="fields?.customer_name" class="col-12 col-md-6 row">
                <div class="col-6">
                  Name on Invoice
                </div>
                <div class="col-6">
                  {{ fields?.customer_name }}
                </div>
              </div>
            </template>
            <div v-else class="col-12 col-md-6 row">
              <div class="col-6">
                {{ fields?.customer_name ? 'Customer' : '' }}
              </div>
              <div class="col-6">
                {{ fields?.customer_name || '' }}
              </div>
            </div>
            <div class="col-12 col-md-6 row">
              <div class="col-6">
                Address
              </div>
              <div class="col-6">
                {{ fields?.address }}
              </div>
            </div>
            <div class="col-12 col-md-6 row">
              <div class="col-6">
                Status
              </div>
              <div class="col-6">
                {{ fields?.status }}
              </div>
            </div>

            <div v-if="fields?.discount_type || fields?.discount_obj" class="col-12 col-md-6 row">
              <div class="col-6">
                Discount
              </div>
              <div class="col-6">
                <template v-if="fields?.discount_obj">
                  <FormattedNumber v-if="fields?.discount_obj.type === 'Amount'" type="currency" :value="fields?.discount_obj.value" />
                  <FormattedNumber
                    v-else-if="fields?.discount_obj.type === 'Percent'"
                    type="unit"
                    unit="percent"
                    :value="fields?.discount_obj.value"
                  />
                </template>
                <template v-else-if="fields?.discount_type">
                  <FormattedNumber v-if="fields?.discount_type === 'Amount'" type="currency" :value="fields?.discount" />
                  <FormattedNumber
                    v-else-if="fields?.discount_type === 'Percent'"
                    type="unit"
                    unit="percent"
                    :value="fields?.discount"
                  />
                </template>
              </div>
            </div>
          </div>
          <div class="col-12 col-md-6 q-gutter-y-lg q-mb-lg">
            <div class="col-12 col-md-6 row">
              <div class="col-6">
                Date
              </div>
              <div class="col-6">
                {{ fields?.date }}
              </div>
            </div>
            <div v-if="fields?.expiry_date" class="col-12 col-md-6 row">
              <div class="col-6">
                Expiry Date
              </div>
              <div class="col-6">
                {{ fields?.expiry_date }}
              </div>
            </div>
            <div v-if="fields?.reference" class="col-12 col-md-6 row">
              <div class="col-6">
                Reference
              </div>
              <div class="col-6">
                {{ fields?.reference }}
              </div>
            </div>
          </div>
        </q-card>
      </q-card>
      <q-card id="to_print" class="q-mx-lg">
        <q-card-section>
          <ViewerTable :fields="fields" />
        </q-card-section>
      </q-card>
      <q-card v-if="fields?.remarks" class="q-mx-lg q-my-md">
        <q-card-section>
          <span class="text-subtitle2 text-grey-9">Remarks: </span>
          <span class="text-grey-9">{{ fields?.remarks }}</span>
        </q-card-section>
      </q-card>
      <div v-if="fields" class="q-px-lg q-pb-lg q-mt-md row justify-between q-gutter-x-md d-print-none">
        <div>
          <div class="row q-gutter-x-md q-gutter-y-md q-mb-md">
            <q-btn
              v-if="checkPermissions('quotations.update')"
              color="orange-5"
              icon="edit"
              label="Edit"
              :to="`/${$route.params.company}/sales/quotations/${fields?.id}/edit`"
            />
          </div>
        </div>
        <div class="row q-gutter-x-md q-gutter-y-md q-mb-md justify-end">
          <q-btn icon="print" label="Print" @click="() => print(false)" />
          <q-btn icon="print" label="Print Body" @click="() => print(true)" />
          <!-- <q-btn
            v-if="isLoggedIn && fields.status !== 'Draft'"
            data-testid="send-email"
            label="Send email"
            @click="isEmailInvoiceModalOpen = true"
          /> -->
          <q-btn
            v-if="
              isLoggedIn && fields.status !== 'Draft' && fields.status !== 'Converted'
                && checkPermissions('quotations.update')
            "
            data-testid="convert-to-invoice"
            label="Convert"
            @click="isConvertModalOpen = true"
          />
          <q-btn
            v-if="
              isLoggedIn && fields.sales_invoice_id
                && checkPermissions('sales.view')
            "
            data-testid="view-sales"
            label="View Sales Invoice"
            :to="`/${$route.params.company}/sales/vouchers/${fields?.sales_invoice_id}`"
          />
        </div>
      </div>
    </div>

    <q-dialog v-model="isEmailInvoiceModalOpen" @hide="resetEmailInvoicePayload">
      <q-card style="min-width: min(60vw, 800px)">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6 flex justify-between">
            <span class="q-mx-md">Send quotation in email</span>
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

    <q-dialog v-model="isConvertModalOpen">
      <q-card style="min-width: min(60vw, 800px)">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6 flex justify-between">
            <span class="q-mx-md">Convert to Sales Voucher?</span>
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
          <!-- message -->
          <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500">
            Are you sure you want to convert this quotation to a sales voucher?
          </div>
          <div class="row justify-end">
            <q-btn
              class="q-mt-md"
              color="orange-5"
              label="Convert"
              @click="convertToInvoice"
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
