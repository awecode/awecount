<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Payment Receipt</span>
          <span v-else>Update Payment Receipt</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12 row no-wrap">
              <span style="flex-grow: 1"><q-input v-model="fields.invoice_nos" label="For Invoice(s)" disable
                  :error-message="errors.invoices" :error="!!errors.invoices">
                </q-input></span>
              <span class="row items-center q-ml-sm" style="flex-grow: 0; flex-shrink: 0"><q-btn icon="add" color="blue"
                  @click="() => (addInoviceModal = !addInoviceModal)">
                </q-btn></span>
            </div>
            <q-input class="col-md-6 col-12" label="Party" v-model="fields.party_name" disable>
            </q-input>
          </div>
          <div class="row q-col-gutter-md">
            <DatePicker class="col-md-6 col-12" label="Deposit Date*" v-model="fields.date"></DatePicker>
            <q-select v-model="fields.mode" label="Mode" class="col-12 col-md-6" :error-message="errors.mode"
              :error="!!errors.mode" :options="['Cheque', 'Cash', 'Bank Deposit']"></q-select>
          </div>
          <div class="row q-col-gutter-md">
            <q-input class="col-md-6 col-12" label="Amount" type="number" v-model="fields.amount"
              :error-message="errors.amount" :error="!!errors.amount"></q-input>
            <q-input class="col-md-6 col-12" label="TDS Amount" v-model="fields.tds_amount"
              :error-message="errors.tds_amount" :error="!!errors.tds_amount" type="number"></q-input>
          </div>
          <div v-if="fields.mode === 'Bank Deposit' || fields.mode === 'Cheque'" class="row q-col-gutter-md">
            <q-select class="col-md-6 col-12" label="Bank Accounts" v-model="fields.bank_account"
              :error-message="errors.bank_account" :error="!!errors.bank_account"
              :options="formDefaults.collections?.bank_accounts" option-value="id" option-label="name" map-options
              emit-value></q-select>
          </div>
          <div v-if="fields.mode === 'Cheque'">
            <div class="row q-col-gutter-md">
              <DatePicker class="col-md-6 col-12" label="Cheque Date" v-model="fields.cheque_date"></DatePicker>
              <q-input class="col-md-6 col-12" label="Cheque Number" v-model="fields.cheque_number"
                :error-message="errors.cheque_number" :error="!!errors.cheque_number" type="number"></q-input>
            </div>
            <q-input v-model="fields.drawee_bank" label="Drawee Bank" type="textarea" autogrow class="col-12 col-md-10"
              :error="!!errors?.drawee_bank" :error-message="errors?.drawee_bank" />
          </div>
          <q-input v-model="fields.remarks" label="Remarks" type="textarea" autogrow class="col-12 col-md-10"
            :error="!!errors?.remarks" :error-message="errors?.remarks" />
        </q-card-section>
      </q-card>
      <div class="q-ma-md row q-pb-lg">
        <q-btn @click.prevent="() => onSubmitClick('Issued', fields, submitForm)" color="green-8"
          :label="isEdit ? 'Update' : 'Create'" />
      </div>
    </q-card>
    <q-dialog v-model="addInoviceModal">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-grey-4">
          <div class="text-h6">
            <span class="q-mx-md">Add Invoice</span>
          </div>
        </q-card-section>

        <q-card-section class="q-mb-md">
          <div class="q-mt-lg q-mx-md">
            <q-input v-model="invoiceFormData.invoice_no" label="Invoice No.*" class="col-12">
            </q-input>
            <div class="q-mx-0 q-my-md">
              <q-checkbox v-model="invoiceFormData.tax_deducted_at_source" label="Tax Deducted at Source?" />
            </div>
            <q-select label="Fiscal Year" v-model="invoiceFormData.fiscal_year"
              :options="formDefaults.options?.fiscal_years" option-value="id" option-label="name" map-options
              emit-value></q-select>
          </div>
          <div class="row q-mt-lg justify-end">
            <q-btn label="Add" color="green" class="q-mt-md" @click="() => fetchInvoice(fields)"></q-btn>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const endpoint = '/v1/payment-receipt/'
    const $q = useQuasar()
    const addInoviceModal = ref(false)
    const invoiceFormData = ref({
      fiscal_year: null,
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
        title:
          (formData.isEdit?.value
            ? 'Payment Receipts Update'
            : 'Payment Receipts Add') + ' | Awecount',
      }
    })
    const onSubmitClick = (status, fields, submitForm) => {
      fields.status = status
      submitForm()
    }
    const fetchInvoice = async (fields) => {
      if (
        invoiceFormData.value.invoice_no &&
        invoiceFormData.value.fiscal_year
      ) {
        const url = `/v1/payment-receipt/fetch-invoice/?fiscal_year=${invoiceFormData.value.fiscal_year}&invoice_no=${invoiceFormData.value.invoice_no}`
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
            } else if (fields.party_id === data.party_id) {
              if (!fields.invoice_nos) fields.invoice_nos = []
              fields.invoice_nos.push(data.voucher_no)
              fields.invoices.push(data.id)
              let invoice_tds = 0
              if (invoiceFormData.value.tax_deducted_at_source) {
                invoice_tds = data.taxable * 0.015
              }
              fields.tds_amount += invoice_tds
              fields.amount =
                (fields.amount || 0) + data.amount - (invoice_tds || 0)
              addInoviceModal.value = false
            } else {
              $q.notify({
                color: 'red-6',
                message:
                  'A single payment receipt can be issued to a single party only!',
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
            if (err.status === 400 && err.data?.detail === 'Invoice has already been paid for!') {
              $q.notify({
                color: 'red-6',
                message: 'Invoice has already been paid for!',
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
    }
  },
}
</script>
