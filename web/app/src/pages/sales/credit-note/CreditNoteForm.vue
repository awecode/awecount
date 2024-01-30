<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Credit Note | Draft</span>
          <span v-else>Update Credit Note | <span v-if="isEdit"> {{ fields?.status }} | <span v-if="fields?.voucher_no"> #
                {{ fields?.voucher_no }}</span></span></span>
        </div>
      </q-card-section>
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12" v-if="fields.invoice_data && fields.invoice_data.length > 0">
              <q-input v-model="fields.invoice_data[0].voucher_no" disable label="Reference Invoice(s)"></q-input>
            </div>
            <div v-else class="col-md-6 col-12">
              <q-btn color="blue" label="Add Refrence" @click="() => (addRefrence = true)" />
              <q-dialog v-model="addRefrence"
                @before-hide="errors && delete errors?.fiscal_year && delete errors?.invoice_no">
                <q-card style="min-width: min(60vw, 400px)">
                  <q-card-section class="bg-grey-4 flex justify-between">
                    <div class="text-h6">
                      <span>Add Reference Invoice(s)</span>
                    </div>
                    <q-btn icon="close" class="text-white bg-red-500 opacity-95" flat round dense v-close-popup />
                  </q-card-section>

                  <q-card-section class="q-mx-lg">
                    <q-input v-model="referenceFormData.invoice_no" label="Invoice No.*" autofocus type="number"
                      :error="!!errors?.invoice_no" :error-message="errors?.invoice_no"></q-input>
                    <q-select class="q-mt-md" label="Fiscal Year" v-model="referenceFormData.fiscal_year"
                      :options="formDefaults.options.fiscal_years" option-value="id" option-label="name" map-options
                      emit-value :error="!!errors?.fiscal_year" :error-message="errors?.fiscal_year"></q-select>
                    <div class="row justify-end q-mt-lg">
                      <q-btn color="green" label="Add" size="md" @click="() => fetchInvoice(fields)"></q-btn>
                    </div>
                  </q-card-section>
                </q-card>
              </q-dialog>
            </div>
            <date-picker v-model="fields.date" class="col-md-6 col-12" label="Date *" :error="!!errors?.date"
              :error-message="errors?.date"></date-picker>
          </div>
          <div class="row q-col-gutter-xl">
            <div class="col-md-6 col-12 row q-col-gutter-md">
              <div :class="fields.discount_type === 'Amount' ||
                fields.discount_type === 'Percent'
                ? 'col-4'
                : 'col-12'
                ">
                <n-auto-complete v-model="fields.discount_type" label="Discount" :error="errors?.discount_type"
                  :error-message="errors?.discount_type" :options="discountOptionsComputed"
                  :modal-component="checkPermissions('SalesDiscountCreate') ? SalesDiscountForm : null">
                </n-auto-complete>
              </div>
              <div class="col-8 row" v-if="fields.discount_type === 'Amount' ||
                fields.discount_type === 'Percent'
                ">
                <q-input class="col-6" v-model.number="fields.discount" label="Discount" :error-message="errors?.discount"
                  :error="!!errors?.discount"></q-input>
                <q-checkbox v-model="fields.trade_discount" label="Trade Discount?" class="col-6">
                </q-checkbox>
              </div>
            </div>
            <div class="row col-md-6 col-12">
              <q-select v-model="fields.mode" label="Mode *" class="col-12" :error-message="errors?.mode"
                :error="!!errors?.mode" :options="staticOptions.modes.concat(
                  formDefaults.collections?.bank_accounts
                )
                  " option-value="id" option-label="name" map-options emit-value>
                <template v-slot:append>
                  <q-icon v-if="fields.mode !== null" class="cursor-pointer" name="clear"
                    @click.stop.prevent="fields.mode = null" /></template></q-select>
            </div>
          </div>
        </q-card-section>
      </q-card>
      <invoice-table :itemOptions="formDefaults.collections ? formDefaults.collections.items : null
        " :unitOptions="formDefaults.collections ? formDefaults.collections.units : null
    " :discountOptions="discountOptionsComputed" :taxOptions="formDefaults.collections?.tax_schemes"
        v-model="fields.rows" :mainDiscount="{
          discount_type: fields.discount_type,
          discount: fields.discount,
        }" :errors="!!errors?.rows ? errors?.rows : null" @deleteRowErr="(index) => deleteRowErr(index, errors, deleteObj)"
        :usedIn="'creditNote'" @updateVoucherMeta="updateVoucherMeta"></invoice-table>
      <div class="row q-px-lg">
        <div class="col-12 col-md-6 row">
          <!-- <q-input
            v-model="fields.remarks"
            label="Remarks"
            type="textarea"
          ></q-input> -->
          <q-input v-model="fields.remarks" label="Remarks" type="textarea" autogrow class="col-12 col-md-10"
            :error="!!errors?.remarks" :error-message="errors?.remarks" />
        </div>
        <div class="col-12 col-md-6 row justify-between">
          <div>
            <q-checkbox label="Export?" v-model="fields.is_export" class="q-mt-md col-3"></q-checkbox>
          </div>
          <q-select v-model="fields.sales_agent" label="Sales Agent" class="col-8" :error="!!errors?.sales_agent"
            :error-message="errors?.sales_agent"></q-select>
          <!-- TODO: add sales agent form -->
        </div>
      </div>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn v-if="checkPermissions('CreditNoteCreate') && (!isEdit || isEdit && fields.status === 'Draft')"
          :loading="loading" @click.prevent="() => onSubmitClick('Draft')" color="orange"
          :label="isEdit ? 'Update Draft' : 'Save Draft'" :disabled="!(fields.invoices && fields.invoices.length > 0)"
          type="submit" />
        <q-btn
          @click.prevent="() => onSubmitClick(isEdit ? fields.status === 'Draft' ? 'Issued' : fields.status : 'Issued')"
          color="green" :loading="loading"
          :label="isEdit ? fields?.status === 'Issued' ? 'Update' : fields?.status === 'Draft' ? 'Issue from Draft' : 'Update' : 'Issue'"
          :disabled="!(fields.invoice_data && fields.invoice_data.length > 0)" />
      </div>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import CategoryForm from '/src/pages/account/category/CategoryForm.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import SalesDiscountForm from 'src/pages/sales/discount/SalesDiscountForm.vue'
import InvoiceTable from 'src/components/voucher/InvoiceTable.vue'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import checkPermissions from 'src/composables/checkPermissions'
import { useLoginStore } from 'src/stores/login-info'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const store = useLoginStore()
    const endpoint = '/v1/credit-note/'
    const openDatePicker = ref(false)
    const addRefrence = ref(false)
    const discountField = ref(null)
    const referenceFormData = ref({
      invoice_no: null,
      fiscal_year: store.companyInfo?.current_fiscal_year_id || null,
    })
    const $q = useQuasar()
    const staticOptions = {
      discount_types: discount_types,
      modes: modes,
    }
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/credit-note/list/',
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value ? 'Credit Note Update' : 'Credit Note Add') +
          ' | Awecount',
      }
    })
    const partyMode = ref(false)
    const switchMode = (fields) => {
      if (fields.mode !== 'Credit') {
        partyMode.value = !partyMode.value
      } else
        $q.notify({
          color: 'orange-4',
          message: 'Credit customer must be a party!',
        })
    }
    const deleteRowErr = (index, errors, deleteObj) => {
      if (deleteObj) {
        if (!formData.fields.value.deleted_rows) {
          formData.fields.value.deleted_rows = []
        }
        formData.fields.value.deleted_rows.push(deleteObj)
      }
      if (!!errors.rows) errors.rows.splice(index, 1)
      // errors.rows.splice(index, 1)
    }
    const onSubmitClick = async (status) => {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      try { await formData.submitForm() } catch (err) {
        formData.fields.value.status = originalStatus
      }
    }
    watch(
      () => formData.fields,
      (newValue) => {
        console.log('dis type', newValue)
      }
    )
    const fetchInvoice = async (fields) => {
      if (!formData?.errors?.value) formData.errors.value = {}
      delete formData.errors.value.fiscal_year
      delete formData.errors.value.invoice_no
      if (
        referenceFormData.value.invoice_no &&
        referenceFormData.value.fiscal_year
      ) {
        const url = 'v1/sales-voucher/by-voucher-no/'
        useApi(
          url +
          `?invoice_no=${referenceFormData.value.invoice_no}&fiscal_year=${referenceFormData.value.fiscal_year}`
        )
          .then((data) => {
            formData.errors.value = {}
            const response = { ...data }
            if (fields.invoices) {
              fields.invoices.push(data.id)
            } else fields.invoices = [data.id]
            fields.invoice_data = [{
              id: data.id,
              voucher_no: data.voucher_no
            }]
            const removeArr = [
              'id',
              'date',
              'voucher_meta',
              'print_count',
              'issue_datetime',
              'is_export',
              'status',
              'due_date',
              'date',
              'remarks',
            ]
            removeArr.forEach((item) => {
              delete data[item]
            })
            for (const key in data) {
              fields[key] = data[key]
              // if (key === )
            }
            if (response.rows && response.rows.length > 0) {
              fields.rows = []
              response.rows.forEach((row) => {
                row.taxObj = row.tax_scheme
                if (row.discount_type === '') {
                  row.discount_type = null
                }
                fields.rows.push(row)
              })
            }
            if (data.discount_obj && data.discount_obj.id) {
              fields.discount_type = data.discount_obj.id
            }
            addRefrence.value = false
          })
          .catch((err) => {
            let message
            if (err.status === 404) message = 'Invoice Not Found!'
            else message = err.data?.detail || 'Server Error! Please contact us with the problem.'
            $q.notify({
              color: 'red-6',
              message: message,
              icon: 'report_problem',
              position: 'top-right',
            })
          })
      } else {
        if (!referenceFormData.value.invoice_no) {
          formData.errors.value.invoice_no = 'Invoice Number is required!'
        }
        if (!referenceFormData.value.fiscal_year) {
          formData.errors.value.fiscal_year = 'Fiscal Year is required!'
        }
        $q.notify({
          color: 'red-6',
          message: 'Please fill in the form completely!',
          icon: 'report_problem',
          position: 'top-right',
        })
      }
    }
    formData.fields.value.date = formData.today
    formData.fields.value.is_export = false
    formData.fields.value.mode = 'Credit'
    formData.fields.value.party = ''
    formData.fields.value.discount_type = null
    formData.fields.value.trade_discount = false

    // to update voucher meta in Credit and debit Notes
    const updateVoucherMeta = (data) => {
      formData.fields.value.discount = data.discount
      formData.fields.value.meta_discount = data.discount
      formData.fields.value.meta_sub_total = data.subTotal
      formData.fields.value.meta_tax = data.totalTax
      formData.fields.value.total_amount = data.total
    }
    const discountOptionsComputed = computed(() => {
      if (formData?.formDefaults.value?.collections?.discounts) {
        return staticOptions.discount_types.concat(
          formData.formDefaults.value.collections.discounts
        )
      } else return staticOptions.discount_types
    })
    return {
      ...formData,
      CategoryForm,
      PartyForm,
      SalesDiscountForm,
      openDatePicker,
      staticOptions,
      InvoiceTable,
      partyMode,
      switchMode,
      deleteRowErr,
      onSubmitClick,
      addRefrence,
      fetchInvoice,
      referenceFormData,
      discountField,
      checkPermissions,
      updateVoucherMeta,
      discountOptionsComputed
    }
  },
}
</script>
