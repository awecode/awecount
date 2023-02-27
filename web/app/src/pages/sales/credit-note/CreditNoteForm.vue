<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Sales Invoice | Draft</span>
          <span v-else>Update Account</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <q-btn
                color="blue"
                label="Add Refrence"
                @click="() => (addRefrence = true)"
              />
              <q-dialog v-model="addRefrence">
                <q-card style="min-width: max(30vw, 500px)">
                  <q-card-section class="bg-grey-4">
                    <div class="text-h6">
                      <span>Add Reference Invoice(s)</span>
                    </div>
                  </q-card-section>
                  <q-separator inset />
                  <q-card-section class="q-ma-lg">
                    <q-input
                      v-model="referenceFormData.invoice_no"
                      label="Invoice No.*"
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
            <q-input
              class="col-md-6 col-12"
              label="Deposit Date*"
              v-model="fields.date"
              disable
            >
            </q-input>
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.address"
              class="col-md-6 col-12"
              label="Address"
              :error-message="errors.address"
              :error="!!errors.address"
            ></q-input>
            <div class="col-md-6 col-12 row q-col-gutter-md">
              <div
                :class="
                  fields.discount_type === 'Amount' ||
                  fields.discount_type === 'Percent'
                    ? 'col-8'
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
              <div
                class="col-4"
                v-if="
                  fields.discount_type === 'Amount' ||
                  fields.discount_type === 'Percent'
                "
              >
                <q-input
                  v-model.number="fields.discount"
                  label="Discount"
                  :error-message="errors.discount"
                  :error="!!errors.discount"
                ></q-input>
              </div>
            </div>
          </div>
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
        @deleteRowErr="(index) => deleteRowErr(index, errors)"
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
            :error="!!error?.remarks"
            :error-message="error?.remarks"
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
            :error="!!error?.sales_agent"
            :error-message="error?.sales_agent"
          ></q-select>
          <!-- TODO: add sales agent form -->
        </div>
      </div>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn
          @click.prevent="() => onSubmitClick('Draft')"
          color="primary"
          label="Draft"
        />
        <q-btn
          @click.prevent="() => onSubmitClick('Issued')"
          color="green-8"
          :label="isEdit ? 'Update' : 'Issue'"
        />
      </div>
      {{ fields.discount_obj }}--disobj <br />
      {{ fields.discount_type }}--distype <br />
      {{ fields.discount }} --discount
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
    const endpoint = '/v1/credit-note/'
    const openDatePicker = ref(false)
    const addRefrence = ref(false)
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
      successRoute: '/account/',
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
    const deleteRowErr = (index, errors) => {
      errors.rows.splice(index, 1)
    }
    const onSubmitClick = (status) => {
      fields.status = status
      // submitForm()
    }
    watch(
      () => fields.discount_type,
      (newValue) => {
        if (typeof newValue === 'number') {
          // const index = formDefaults
        }
      }
    )
    const fetchInvoice = async (fields) => {
      if (
        referenceFormData.value.invoice_no &&
        referenceFormData.value.fiscal_year
      ) {
        const url = 'v1/sales-voucher/by-voucher-no/'
        // try {
        //   const response =
        // } catch (error) {
        //   console.log(error, 'elol')
        //   if (error.response.status === 404) {
        //     $q.notify({
        //       color: 'red-6',
        //       message: 'Invoice not found!',
        //       icon: 'report_problem',
        //       position: 'top-right',
        //     })
        //   }
        // }
        useApi(
          url +
            `?invoice_no=${referenceFormData.value.invoice_no}&fiscal_year=${referenceFormData.value.fiscal_year}`
        )
          .then((data) => {
            if (fields.invoices) {
              fields.invoices.push(data.id)
            } else fields.invoices = [data.id]
            debugger
            console.log(data, fields)
            fields.date = data.date
            fields.discount_type = data.discount_type
            const newData = {
              id: data.id,
              date: data.date,
              // "voucher_meta",
              // "print_count",
              // "issue_datetime",
              // "is_export",
              // "status",
              // "due_date",
              // "date",
              // "remarks"
            }
          })
          .catch((err) => console.log('elol', err.status))
        // .then(({ data }) => {
        //   this.fields.invoices.push(data.id)
        //   ;[
        //     'id',
        //     'date',
        //     'voucher_meta',
        //     'print_count',
        //     'issue_datetime',
        //     'is_export',
        //     'status',
        //     'due_date',
        //     'date',
        //     'remarks',
        //   ].forEach((key) => {
        //     delete data[key]
        //   })
        //   data.rows.forEach((row) => {
        //     delete row['id']
        //     if (row.discount_obj && row.discount_obj.id) {
        //       row.discount_type = row.discount_obj.id
        //     }
        //   })
        //   this.$vue.set(this, 'fields', Object.assign({}, this.fields, data))
        //   if (data.discount_obj && data.discount_obj.id) {
        //     this.fields.discount_type = data.discount_obj.id
        //   }
        //   this.options.sales_invoice_objs.push(data)
        // })
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
    }
  },
}
</script>
