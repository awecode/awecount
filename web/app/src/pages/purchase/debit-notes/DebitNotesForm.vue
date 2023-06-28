<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Debit Note | Draft</span>
          <span v-else>Update Debit Note</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12" v-if="fields.invoices">
              <q-input v-model="fields.invoices" disable label="Reference Invoice(s)"></q-input>
            </div>
            <div v-else class="col-md-6 col-12">
              <q-btn color="blue" label="Add Refrence" @click="() => (addRefrence = true)" />
              <q-dialog v-model="addRefrence">
                <q-card style="min-width: min(60vw, 400px)">
                  <q-card-section class="bg-grey-4">
                    <div class="text-h6">
                      <span>Add Reference Invoice(s)</span>
                    </div>
                  </q-card-section>
                  <q-card-section class="q-mx-lg">
                    <q-input v-model="referenceFormData.invoice_no" label="Invoice No.*"></q-input>
                    <q-select class="q-mt-md" label="Party*" v-model="referenceFormData.party" :options="partyChoices"
                      option-value="id" option-label="name" map-options emit-value></q-select>
                    <q-select class="q-mt-md" label="Fiscal Year" v-model="referenceFormData.fiscal_year"
                      :options="formDefaults.options.fiscal_years" option-value="id" option-label="name" map-options
                      emit-value></q-select>
                    <div class="row justify-end q-mt-lg">
                      <q-btn color="green" label="Add" size="md" @click="() => fetchInvoice(fields)"></q-btn>
                    </div>
                  </q-card-section>
                </q-card>
              </q-dialog>
            </div>
            <!-- <q-input
              v-model="fields.date"
              class="col-md-6 col-12"
              label="Start Date"
            >
              <template v-slot:append>
                <q-icon name="event" class="cursor-pointer">
                  <q-popup-proxy
                    cover
                    transition-show="scale"
                    transition-hide="scale"
                  >
                    <q-date v-model="fields.date" mask="YYYY-MM-DD">
                      <div class="row items-center justify-end">
                        <q-btn
                          v-close-popup
                          label="Close"
                          color="primary"
                          flat
                        />
                      </div>
                    </q-date>
                  </q-popup-proxy>
                </q-icon>
              </template>
            </q-input> -->
            <date-picker v-model="fields.date" class="col-md-6 col-12" label="Start Date"></date-picker>
          </div>
          <div class="row q-col-gutter-xl">
            <div class="col-md-6 col-12 row q-col-gutter-md">
              <div :class="fields.discount_type === 'Amount' ||
                fields.discount_type === 'Percent'
                ? 'col-4'
                : 'col-12'
                ">
                <n-auto-complete v-model="fields.discount_type" label="Discount*" :error="errors.discount_type" :options="formDefaults.collections
                  ? staticOptions.discount_types.concat(
                    formDefaults?.collections.discounts
                  )
                  : staticOptions.discount_types
                  " :modal-component="SalesDiscountForm">
                </n-auto-complete>
              </div>
              <div class="col-8 row" v-if="fields.discount_type === 'Amount' ||
                fields.discount_type === 'Percent'
                ">
                <q-input class="col-6" v-model.number="fields.discount" label="Discount" :error-message="errors.discount"
                  :error="!!errors.discount"></q-input>
                <q-checkbox v-model="fields.trade_discount" label="Trade Discount?" class="col-6">
                </q-checkbox>
              </div>
            </div>
            <div class="row col-md-6 col-12">
              <q-select v-model="fields.mode" label="Mode" class="col-12" :error-message="errors.mode"
                :error="!!errors.mode" :options="staticOptions.modes.concat(
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
    " :discountOptions="formDefaults.collections
    ? staticOptions.discount_types.concat(
      formDefaults?.collections.discounts
    )
    : staticOptions.discount_types
    " :taxOptions="formDefaults.collections?.tax_schemes" v-model="fields.rows" :mainDiscount="{
    discount_type: fields.discount_type,
    discount: fields.discount,
  }" :errors="!!errors.rows ? errors.rows : null" @deleteRowErr="(index) => deleteRowErr(index, errors, deleteObj)"
        :usedIn="'creditNote'"></invoice-table>
      <div class="row q-px-lg">
        <q-input v-model="fields.remarks" label="Remarks" type="textarea" autogrow class="col-12"
          :error="!!errors?.remarks" :error-message="errors?.remarks" />
      </div>
      <div v-if="checkPermissions('DebitNoteCreate')" class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn v-if="!isEdit" @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" color="orange-8"
          label="Draft" :disable="fields.invoices ? false : true" />
        <q-btn v-if="isEdit && fields.status === 'Draft'"
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" color="orange-8" label="Save Draft"
          :disable="fields.invoices ? false : true" />
        <q-btn @click.prevent="() => onSubmitClick('Issued', fields, submitForm)" color="green-8"
          :label="isEdit ? 'Update' : 'Issue'" :disable="fields.invoices ? false : true" />
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
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const endpoint = '/v1/debit-note/'
    const openDatePicker = ref(false)
    const addRefrence = ref(false)
    const discountField = ref(null)
    const partyChoices = ref(null)
    const referenceFormData = ref({
      invoice_no: null,
      fiscal_year: null,
    })
    const $q = useQuasar()
    const staticOptions = {
      discount_types: discount_types,
      modes: modes,
    }
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/debit-note/list/',
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value ? 'Debit Notes Update' : 'Debit Notes Add') +
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
    const onSubmitClick = (status, fields, submitForm) => {
      fields.status = status
      submitForm()
    }
    // watch(
    //   () => formData.fields,
    //   (newValue) => {
    //     console.log('dis type', newValue)
    //   }
    // )
    const fetchInvoice = (fields) => {
      if (
        referenceFormData.value.invoice_no &&
        referenceFormData.value.fiscal_year &&
        referenceFormData.value.party
      ) {
        const url = 'v1/purchase-vouchers/by-voucher-no/'
        useApi(
          url +
          `?invoice_no=${referenceFormData.value.invoice_no}&fiscal_year=${referenceFormData.value.fiscal_year}&party=${referenceFormData.value.party}`
        )
          .then((data) => {
            if (fields.invoices) {
              fields.invoices.push(data.id)
            } else fields.invoices = [data.id]
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
            if (data.discount_obj && data.discount_obj.id) {
              fields.discount_type = data.discount_obj.id
            }
            addRefrence.value = false
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
            // addRefrence.value = false
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
    formData.fields.value.is_export = false
    formData.fields.value.mode = 'Credit'
    formData.fields.value.party = ''
    formData.fields.value.discount_type = null
    formData.fields.value.trade_discount = false
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
      partyChoices,
      checkPermissions
    }
  },
  created() {
    useApi('/v1/parties/choices/')
      .then((res) => {
        this.partyChoices = res
      })
      .catch((err) => {
        console.log('error fetching choices due to', err)
      })
  },
}
</script>
