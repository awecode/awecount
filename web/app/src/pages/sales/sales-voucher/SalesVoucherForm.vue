<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Sales Invoice | Draft</span>
          <span v-else>Update Sale Invoice | Draft</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div
              class="col-md-6 col-12"
              v-if="formDefaults.options?.enable_import_challan"
            >
              <q-btn
                color="blue"
                @click="importChallanModal = true"
                label="Import challan(s)"
              ></q-btn>
              <div v-if="fields.invoices">
                <q-input
                  dense
                  v-model="fields.invoices"
                  disable
                  label="Import challan(s)"
                ></q-input>
              </div>
              <q-dialog v-model="importChallanModal">
                <q-card style="min-width: min(60vw, 400px)">
                  <q-card-section class="bg-grey-4">
                    <div class="text-h6">
                      <span>Add Reference Challan(s)</span>
                    </div>
                  </q-card-section>
                  <q-separator inset />
                  <q-card-section class="q-mx-lg">
                    <q-input
                      v-model.number="referenceFormData.invoice_no"
                      label="Challan No.*"
                    ></q-input>
                    <q-select
                      class="q-mt-md"
                      label="Fiscal Year"
                      v-model="referenceFormData.fiscal_year"
                      :options="formDefaults.options.fiscal_years"
                      option-value="id"
                      option-label="name"
                      map-options
                      emit-value
                    ></q-select>
                    <div class="row justify-end q-mt-lg">
                      <q-btn
                        color="green"
                        label="Add"
                        size="md"
                        @click="() => fetchInvoice(fields)"
                      ></q-btn>
                    </div>
                  </q-card-section>
                </q-card>
              </q-dialog>
            </div>
            <div class="col-md-6 col-12">
              <div class="row">
                <div class="col-10">
                  <q-input
                    v-model="fields.customer_name"
                    label="Customer Name"
                    :error-message="errors.customer_name"
                    :error="!!errors.customer_name"
                    v-if="partyMode && fields.mode !== 'Credit'"
                  >
                  </q-input>
                  <n-auto-complete
                    v-else
                    v-model="fields.party"
                    :options="formDefaults.collections?.parties"
                    label="Party"
                    :error="errors?.party ? errors?.party : null"
                    :modal-component="PartyForm"
                  />
                </div>
                <div class="col-2 row justify-center q-py-md">
                  <q-btn flat size="md" @click="() => switchMode(fields)">
                    <q-icon name="mdi-account-group"></q-icon>
                  </q-btn>
                </div>
              </div>
              <div></div>
            </div>
            <q-input
              class="col-md-6 col-12"
              label="Deposit Date*"
              v-model="fields.date"
              disable
            >
            </q-input>
            <q-input
              v-model="fields.address"
              class="col-md-6 col-12"
              label="Address"
              :error-message="errors.address"
              :error="!!errors.address"
            ></q-input>
            <date-picker
              v-if="formDefaults.options?.enable_due_date_in_voucher"
              label="Due Date"
              v-model="fields.due_date"
              class="col-md-6 col-12"
              :error-message="errors.due_date"
              :error="!!errors.due_date"
            ></date-picker>
            <div class="col-md-6 col-12 row q-col-gutter-md">
              <div
                :class="
                  ['Percent', 'Amount'].includes(fields.discount_type)
                    ? 'col-6'
                    : 'col-12'
                "
              >
                <n-auto-complete
                  v-model="fields.discount_type"
                  label="Discount*"
                  :error="errors.discount_type"
                  :error-message="errors.discount_type"
                  :options="
                    formDefaults.collections
                      ? staticOptions.discount_types.concat(
                          formDefaults?.collections.discounts
                        )
                      : staticOptions.discount_types
                  "
                  :modal-component="SalesDiscountForm"
                >
                </n-auto-complete>
              </div>
              <div class="col-6 row">
                <div
                  :class="
                    formDefaults.options?.show_trade_discount_in_voucher
                      ? 'col-6'
                      : 'col-12'
                  "
                  v-if="
                    fields.discount_type === 'Amount' ||
                    fields.discount_type === 'Percent'
                  "
                >
                  <q-input
                    class="col-6"
                    v-model.number="fields.discount"
                    label="Discount"
                    :error-message="errors.discount"
                    :error="!!errors.discount"
                  ></q-input>
                </div>
                <div
                  class="col-3 row"
                  v-if="
                    formDefaults.options?.show_trade_discount_in_voucher &&
                    ['Percent', 'Amount'].includes(fields.discount_type)
                  "
                >
                  <q-checkbox
                    v-model="fields.trade_discount"
                    label="Trade Discount?"
                  ></q-checkbox>
                </div>
              </div>
            </div>
          </div>
          <!-- <div class="row q-col-gutter-md"></div> -->
          <div class="row q-col-gutter-md">
            <q-select
              v-model="fields.mode"
              label="Mode"
              class="col-12 col-md-6"
              :error-message="errors.mode"
              :error="!!errors.mode"
              :options="
                staticOptions.modes.concat(
                  formDefaults.collections?.bank_accounts
                )
              "
              option-value="id"
              option-label="name"
              map-options
              emit-value
            >
              <template v-slot:append>
                <q-icon
                  v-if="fields.mode !== null"
                  class="cursor-pointer"
                  name="clear"
                  @click.stop.prevent="fields.mode = null" /></template
            ></q-select>
          </div>
        </q-card-section>
      </q-card>
      <invoice-table
        :itemOptions="
          formDefaults.collections ? formDefaults.collections.items : null
        "
        :unitOptions="
          formDefaults.collections ? formDefaults.collections.units : null
        "
        :discountOptions="
          formDefaults.collections
            ? staticOptions.discount_types.concat(
                formDefaults?.collections.discounts
              )
            : staticOptions.discount_types
        "
        :taxOptions="formDefaults.collections?.tax_schemes"
        v-model="fields.rows"
        :mainDiscount="{
          discount_type: fields.discount_type,
          discount: fields.discount,
        }"
        :errors="!!errors.rows ? errors.rows : null"
        @deleteRowErr="
          (index, deleteObj) => deleteRowErr(index, errors, deleteObj)
        "
        :enableRowDescription="formDefaults.options?.enable_row_description"
        :showRowTradeDiscount="formDefaults.options?.show_trade_discount_in_row"
      ></invoice-table>
      <div class="row q-px-lg">
        <div class="col-12 col-md-6 row">
          <!-- <q-input
            v-model="fields.remarks"
            label="Remarks"
            type="textarea"
          ></q-input> -->
          <q-input
            v-model="fields.remarks"
            label="Remarks"
            type="textarea"
            autogrow
            class="col-12 col-md-10"
            :error="!!errors?.remarks"
            :error-message="errors?.remarks"
          />
        </div>
        <div class="col-12 col-md-6 row justify-between">
          <div>
            <q-checkbox
              label="Export?"
              v-model="fields.is_export"
              class="q-mt-md col-3"
            ></q-checkbox>
          </div>
          <q-select
            v-model="fields.sales_agent"
            label="Sales Agent"
            class="col-8"
            :error="!!errors?.sales_agent"
            :error-message="errors?.sales_agent"
          ></q-select>
          <!-- TODO: add sales agent form -->
        </div>
      </div>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)"
          color="primary"
          label="Draft"
        />
        <q-btn
          @click.prevent="() => onSubmitClick('Issued', fields, submitForm)"
          color="green-8"
          :label="isEdit ? 'Update' : 'Issue'"
        />
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
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const endpoint = '/v1/sales-voucher/'
    const openDatePicker = ref(false)
    const $q = useQuasar()
    const importChallanModal = ref(false)
    const referenceFormData = ref({
      invoice_no: null,
      fiscal_year: null,
    })
    const staticOptions = {
      discount_types: discount_types,
      modes: modes,
    }
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/sales-voucher/list/',
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value
            ? 'Sales Invoice Update'
            : 'Sales Invoice Add') + ' | Awecount',
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
    }
    const onSubmitClick = (status, fields, submitForm) => {
      fields.status = status
      submitForm()
    }
    formData.fields.value.due_date = formData.today
    formData.fields.value.date = formData.today
    formData.fields.value.mode = 'Credit'
    formData.fields.value.is_export = false

    const fetchInvoice = async (fields) => {
      if (
        referenceFormData.value.invoice_no &&
        referenceFormData.value.fiscal_year
      ) {
        if (
          fields.invoices &&
          fields.invoices.includes(referenceFormData.value.invoice_no)
        ) {
          $q.notify({
            color: 'red-6',
            message: 'Invoice Already Exists!',
            icon: 'report_problem',
            position: 'top-right',
          })
        } else {
          const url = 'v1/challan/by-voucher-no/'
          useApi(
            url +
              `?invoice_no=${referenceFormData.value.invoice_no}&fiscal_year=${referenceFormData.value.fiscal_year}`
          )
            .then((data) => {
              const response = { ...data }
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
                'rows',
                'date',
                'remarks',
              ]
              if (data.customer_name) {
                partyMode.value = true
                fields.mode = 'Cash'
              }
              if (data.party) {
                partyMode.value = false
                fields.mode = 'Credit'
              }
              removeArr.forEach((item) => {
                delete data[item]
              })
              for (const key in data) {
                fields[key] = data[key]
                // if (key === )
              }
              // debugger
              if (response.rows && response.rows.length > 0) {
                // debugger
                if (fields.rows) {
                  response.rows.forEach((row) => {
                    fields.rows.push(row)
                  })
                } else {
                  fields.rows = response.rows
                }
              }
              if (data.discount_obj && data.discount_obj.id) {
                fields.discount_type = data.discount_obj.id
              }
              importChallanModal.value = false
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
            })
        }
      } else {
        $q.notify({
          color: 'red-6',
          message: 'Please fill in the form completely!',
          icon: 'report_problem',
          position: 'top-right',
        })
      }
    }
    // partyMode.value = formData.formDefaults.value.options.show_customer

    // watch(
    //   () => formData.fields.value.party,
    //   (newValue) => {
    //     console.log(newValue)
    //     if (!!newValue && !!formData.formDefaults.value.collections) {
    //       const index =
    //         formData.formDefaults.value.collections.parties.findIndex(
    //           (option) => option.id === newValue
    //         )
    //       formData.fields.value.address =
    //         formData.formDefaults.value.collections.parties[index].address
    //       // const index = formDefaults.
    //     }
    //   }
    // )
    // watch(
    //   () => formData,
    //   (newValue) => {
    //     console.log(newValue)
    //   }
    // )

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
      importChallanModal,
      referenceFormData,
      fetchInvoice,
    }
  },
}
</script>
