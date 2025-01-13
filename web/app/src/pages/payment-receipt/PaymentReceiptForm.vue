<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'
import { useLoginStore } from 'src/stores/login-info'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/payment-receipt/`
    const $q = useQuasar()
    const store = useLoginStore()
    const addInoviceModal = ref(false)
    const invoiceFormData = ref({
      fiscal_year: store.companyInfo?.current_fiscal_year_id || null,
      invoice_no: null,
      tax_deducted_at_source: true,
    })
    // const invoice_nos = ref([])
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/payment-receipt/list/',
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Payment Receipts Update' : 'Payment Receipts Add'} | Awecount`,
      }
    })
    const onSubmitClick = (status, fields, submitForm) => {
      fields.status = status
      submitForm()
    }
    const fetchInvoice = async (fields) => {
      if (!formData?.errors?.value) formData.errors.value = {}
      delete formData.errors.value.fiscal_year
      delete formData.errors.value.invoice_no
      if (invoiceFormData.value.invoice_no && invoiceFormData.value.fiscal_year) {
        const url = `/api/company/${route.params.company}/payment-receipt/fetch-invoice/?fiscal_year=${invoiceFormData.value.fiscal_year}&invoice_no=${invoiceFormData.value.invoice_no}`
        useApi(url)
          .then((data) => {
            if (!fields.party_id) {
              fields.party_id = data.party_id
              fields.party_name = data.party_name
            }
            if (fields.invoices.includes(data.id)) {
              $q.notify({
                color: 'red-6',
                message: 'The invoice has already been added!',
                icon: 'report_problem',
                position: 'top-right',
              })
              formData.errors.value.invoice_no = 'The invoice has already been added!'
            } else if (fields.party_id === data.party_id) {
              if (!fields.invoice_nos) fields.invoice_nos = []
              fields.invoice_nos.push(data.voucher_no)
              fields.invoices.push(data.id)
              let invoice_tds = 0
              if (invoiceFormData.value.tax_deducted_at_source) {
                invoice_tds = data.taxable * 0.015
              }
              fields.tds_amount += invoice_tds
              fields.amount = (fields.amount || 0) + data.amount - (invoice_tds || 0)
              addInoviceModal.value = false
            } else {
              $q.notify({
                color: 'red-6',
                message: 'A single payment receipt can be issued to a single party only!',
                icon: 'report_problem',
                position: 'top-right',
              })
            }
          })
          .catch((err) => {
            if (err.status === 404) {
              $q.notify({
                color: 'red-6',
                message: 'Invoice not found!',
                icon: 'report_problem',
                position: 'top-right',
              })
            }
            if (err.status === 400 && err.data?.detail) {
              $q.notify({
                color: 'red-6',
                message: err.data?.detail,
                icon: 'report_problem',
                position: 'top-right',
              })
            }
          })
      } else {
        $q.notify({
          color: 'red-6',
          message: 'Please fill in the form completely!',
          icon: 'report_problem',
          position: 'top-right',
        })
        if (!invoiceFormData.value.invoice_no) {
          formData.errors.value.invoice_no = 'Invoice Number is required!'
        }
        if (!invoiceFormData.value.fiscal_year) {
          formData.errors.value.fiscal_year = 'Fiscal Year is required!'
        }
      }
    }
    formData.fields.value.date = formData.today
    formData.fields.value.cheque_date = formData.today
    formData.fields.value.mode = 'Cheque'
    formData.fields.value.invoices = []
    // formData.fields.value.invoice_nos invoice_nos.value
    formData.fields.value.tds_amount = 0
    formData.fields.value.cleared = false
    return {
      ...formData,
      onSubmitClick,
      addInoviceModal,
      invoiceFormData,
      fetchInvoice,
      checkPermissions,
    }
  },
}
</script>

<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Payment Receipt</span>
          <span v-else>
            Update Payment Receipt
            <span v-if="fields.voucher_no">| # {{ fields.voucher_no }}</span>
          </span>
        </div>
      </q-card-section>
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12 row no-wrap">
              <span style="flex-grow: 1"><q-input v-model="fields.invoice_nos" label="For Invoice(s) *" disable :error-message="errors.invoices" :error="!!errors.invoices" /></span>
              <span class="row items-center q-ml-sm" style="flex-grow: 0; flex-shrink: 0"><q-btn icon="add" color="blue" @click="() => (addInoviceModal = !addInoviceModal)" /></span>
            </div>
            <q-input v-model="fields.party_name" class="col-md-6 col-12" label="Party" disable :error="!!errors?.party_name" :error-message="errors.party_name" />
          </div>
          <div class="row q-col-gutter-md">
            <DatePicker v-model="fields.date" class="col-md-6 col-12" label="Deposit Date*" />
            <q-select v-model="fields.mode" label="Mode" class="col-12 col-md-6" :error-message="errors.mode" :error="!!errors.mode" :options="['Cheque', 'Cash', 'Bank Deposit']" />
          </div>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.amount" class="col-md-6 col-12" label="Amount *" type="number" :error-message="errors.amount" :error="!!errors.amount" />
            <q-input v-model="fields.tds_amount" class="col-md-6 col-12" label="TDS Amount" :error-message="errors.tds_amount" :error="!!errors.tds_amount" type="number" />
          </div>
          <div v-if="fields.mode === 'Bank Deposit' || fields.mode === 'Cheque'" class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <n-auto-complete-v2 v-model="fields.bank_account" label="Bank Account *" :error-message="errors.bank_account" endpoint="/api/company/payment-receipt/create-defaults/bank_accounts" :error="!!errors.bank_account" :static-option="fields.selected_bank_account_obj" :options="formDefaults.collections?.bank_accounts" option-value="id" option-label="name" map-options emit-value />
            </div>
          </div>
          <div v-if="fields.mode === 'Cheque'">
            <div class="row q-col-gutter-md">
              <DatePicker v-model="fields.cheque_date" class="col-md-6 col-12" label="Cheque Date" :not-required="true" :error="!!errors?.cheque_date" :error-message="errors?.cheque_date" />
              <q-input v-model="fields.cheque_number" class="col-md-6 col-12" label="Cheque Number *" :error-message="errors.cheque_number" :error="!!errors.cheque_number" type="number" />
            </div>
            <q-input v-model="fields.drawee_bank" label="Drawee Bank" type="textarea" autogrow class="col-12 col-md-10" :error="!!errors?.drawee_bank" :error-message="errors?.drawee_bank" />
          </div>
          <q-input v-model="fields.remarks" label="Remarks" type="textarea" autogrow class="col-12 col-md-10" :error="!!errors?.remarks" :error-message="errors?.remarks" />

          <div class="q-mt-lg row q-pb-lg flex justify-end">
            <q-btn v-if="checkPermissions('paymentreceipt.create') && !isEdit" :loading="loading" color="green" label="Create" type="submit" @click.prevent="() => onSubmitClick('Issued', fields, submitForm)" />
            <q-btn v-if="checkPermissions('paymentreceipt.modify') && isEdit" :loading="loading" color="green" label="Update" type="submit" @click.prevent="() => onSubmitClick(fields.status, fields, submitForm)" />
          </div>
        </q-card-section>
      </q-card>
    </q-card>
    <q-dialog v-model="addInoviceModal" @before-hide="errors && delete errors?.fiscal_year && delete errors?.invoice_no">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-grey-4 flex justify-between">
          <div class="text-h6">
            <span class="q-mx-md">Add Invoice</span>
          </div>
          <q-btn v-close-popup icon="close" class="text-white bg-red-500 opacity-95" flat round dense />
        </q-card-section>

        <q-card-section class="q-mb-md">
          <div class="q-mt-lg q-mx-md">
            <q-input v-model="invoiceFormData.invoice_no" label="Invoice No.*" class="col-12" autofocus type="number" :error="!!errors?.invoice_no" :error-message="errors?.invoice_no" />
            <div class="q-mx-0 q-my-md">
              <q-checkbox v-model="invoiceFormData.tax_deducted_at_source" label="Tax Deducted at Source?" />
            </div>
            <q-select v-model="invoiceFormData.fiscal_year" label="Fiscal Year" :options="formDefaults.options?.fiscal_years" option-value="id" option-label="name" map-options emit-value :error="!!errors?.fiscal_year" :error-message="errors?.fiscal_year" />
          </div>
          <div class="row q-mt-lg justify-end">
            <q-btn label="Add" color="green" class="q-mt-md" @click="() => fetchInvoice(fields)" />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>
