<template>
  <q-form class="q-pa-lg" autofocus v-if="fields">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6" data-testid="form-title">
          <span v-if="!isEdit">New Sales Invoice | Draft</span>
          <span v-else
            >Update Sale Invoice | {{ fields.status }}
            <span v-if="fields.voucher_no"
              >| # {{ fields.voucher_no }}</span
            ></span
          >
        </div>
      </q-card-section>
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
                data-testid="import-challan-btn"
                label="Import challan(s)"
              ></q-btn>
              <div v-if="fields.challans && fields.challans.length > 0">
                <q-input
                  dense
                  v-model="fields.challan_numbers"
                  disable
                  label="Import challan(s)"
                ></q-input>
              </div>
              <q-dialog v-model="importChallanModal" @before-hide="errors && delete errors?.fiscal_year && delete errors?.invoice_no">
                <q-card style="min-width: min(60vw, 400px)">
                  <q-card-section class="bg-grey-4">
                    <div class="text-h6">
                      <span>Add Reference Challan(s)</span>
                    </div>
                  </q-card-section>

                  <q-card-section class="q-mx-lg">
                    <q-input
                      v-model.number="referenceFormData.invoice_no"
                      label="Challan No.*"
                      autofocus
                      type="number" :error="!!errors?.invoice_no" :error-message="errors?.invoice_no"
                      data-testid="challan-no-input"
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
                      data-testid="fiscal-year-select"
                     :error="!!errors?.fiscal_year" :error-message="errors?.fiscal_year" ></q-select>
                    <div class="row justify-end q-mt-lg">
                      <q-btn
                        color="green"
                        label="Add"
                        size="md"
                        @click="fetchInvoice(fields)"
                        data-testid="add-reference-btn"
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
                    :error-message="errors?.customer_name"
                    :error="!!errors?.customer_name"
                    v-if="partyMode && fields.mode !== 'Credit'"
                    data-testid="customer-name-input"
                  >
                  </q-input>
                  <n-auto-complete
                    v-else
                    v-model="fields.party"
                    :options="formDefaults.collections?.parties"
                    label="Party"
                    :error="errors?.party ? errors?.party : null"
                    :modal-component="
                      checkPermissions('PartyCreate') ? PartyForm : null
                    "
                    @update:modelValue="onPartyChange"
                  />
                </div>
                <div class="col-2 row justify-center q-py-md">
                  <q-btn
                    flat
                    size="md"
                    @click="() => switchMode(fields)"
                    data-testid="switch-account-group-btn"
                  >
                    <q-icon name="mdi-account-group"></q-icon>
                  </q-btn>
                </div>
              </div>
              <div></div>
            </div>
            <date-picker
              v-if="formDefaults.options?.enable_sales_date_edit"
              label="Invoice Date*"
              v-model="fields.date"
              class="col-md-6 col-12"
              :error="!!errors?.date"
              :error-message="errors?.date"
            ></date-picker>
            <DateInputDisabled
              v-else
              :date="fields.date"
              class="col-md-6 col-12"
              label="Invoice Date*"
            />
            <q-input
              v-model="fields.address"
              class="col-md-6 col-12"
              label="Address"
              :error-message="errors?.address"
              :error="!!errors?.address"
              data-testid="address-input"
            ></q-input>
            <date-picker
              v-if="formDefaults.options?.enable_due_date_in_voucher"
              label="Due Date"
              v-model="fields.due_date"
              class="col-md-6 col-12"
              :error="!!errors?.due_date"
              :error-message="errors?.due_date"
              :toLimit="fields.date"
            ></date-picker>
            <div class="col-md-6 col-12 row q-col-gutter-md">
              <div :class="['Percent', 'Amount'].includes(fields.discount_type)
                ? 'col-6'
                : 'col-12'
                " data-testid="overall-discount-type-div">
                <n-auto-complete v-model="fields.discount_type" label="Discount"
                  :error="errors?.discount_type ? errors?.discount_type : null" :options="discountOptionsComputed"
                  :modal-component="checkPermissions('SalesDiscountCreate') ? SalesDiscountForm : null">
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
                    :error-message="errors?.discount"
                    :error="!!errors?.discount"
                    data-testid="discount-input"
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
                    data-testid="trade-discount-input"
                  ></q-checkbox>
                </div>
              </div>
            </div>
          </div>
          <!-- <div class="row q-col-gutter-md"></div> -->
          <div class="row q-col-gutter-md">
            <q-select
              v-model="fields.mode"
              label="Mode *"
              class="col-12 col-md-6"
              :error-message="errors?.mode"
              :error="!!errors?.mode"
              :options="
                staticOptions.modes.concat(
                  formDefaults.collections?.bank_accounts
                )
              "
              option-value="id"
              option-label="name"
              map-options
              emit-value
              data-testid="mode-input"
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
      <invoice-table v-if="formDefaults.collections" :itemOptions="formDefaults.collections ? formDefaults.collections.items : null
        " :unitOptions="formDefaults.collections ? formDefaults.collections.units : null
    " :discountOptions="discountOptionsComputed" :taxOptions="formDefaults.collections?.tax_schemes" v-model="fields.rows" :mainDiscount="{
    discount_type: fields.discount_type,
    discount: fields.discount,
  }" :errors="!!errors?.rows ? errors.rows : null" @deleteRowErr="(index, deleteObj) => deleteRowErr(index, errors, deleteObj)
  " :enableRowDescription="formDefaults.options?.enable_row_description"
        :showRowTradeDiscount="formDefaults.options?.show_trade_discount_in_row" :inputAmount="formDefaults.options?.enable_amount_entry"
        :showRateQuantity="formDefaults.options?.show_rate_quantity_in_voucher" :isFifo="formDefaults.options?.enable_fifo" usedIn="sales"
        :hasChallan="!!(fields.challans && fields.challans.length > 0)"></invoice-table>
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
            data-testid="remarks-input"
          />
        </div>
        <div class="col-12 col-md-6 row justify-between">
          <div>
            <q-checkbox
              label="Export?"
              v-model="fields.is_export"
              class="q-mt-md col-3"
              data-testid="export-checkbox"
            ></q-checkbox>
          </div>
          <q-select
            v-if="loginStore.companyInfo.enable_sales_agents"
            v-model="fields.sales_agent"
            label="Sales Agent"
            class="col-8"
            :error="!!errors?.sales_agent"
            :error-message="errors?.sales_agent"
            :options="formDefaults.collections?.sales_agents"
            option-value="id"
            option-label="name"
            map-options
            emit-value
            data-testid="sales-agent-select"
          ></q-select>
          <!-- TODO: add sales agent form -->
        </div>
      </div>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn v-if="!isEdit && checkPermissions('SalesCreate')" :loading="loading"
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" color="orange-8" label="Save Draft"
          type="submit" class="issue-btn" />
        <q-btn v-if="isEdit && fields.status === 'Draft' && checkPermissions('SalesModify')"
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" :loading="loading" color="orange-8" :label=" isEdit ? 'Update Draft' : 'Save Draft'"
          type="submit" class="draft-btn" />
        <q-btn v-if="checkPermissions('SalesCreate')" :loading="loading" @click.prevent="() => onSubmitClick(isEdit ? fields.status === 'Draft' ? 'Issued' : fields.status : 'Issued', fields, submitForm)"
          color="green" :label="isEdit ? fields?.status === 'Issued' ? 'Update' : fields?.status === 'Draft' ? `Issue # ${formDefaults.options?.voucher_no || 1} from Draft` : 'update' : `Issue # ${formDefaults.options?.voucher_no || 1}`" class="issue-btn" />
      </div>
    </q-card>
  </q-form>
</template>
<script>
import CategoryForm from '/src/pages/account/category/CategoryForm.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import SalesDiscountForm from 'src/pages/sales/discount/SalesDiscountForm.vue'
import InvoiceTable from 'src/components/voucher/InvoiceTable.vue'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import { useLoginStore } from '/src/stores/login-info.js'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const endpoint = '/v1/sales-voucher/'
    const loginStore = useLoginStore()
    const show_row_column_in_voucher_row = true
    // TODO: temp
    const $q = useQuasar()
    const importChallanModal = ref(false)
    const referenceFormData = ref({
      invoice_no: null,
      fiscal_year: loginStore.companyInfo.current_fiscal_year_id || null
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
    const onSubmitClick = async (status, fields, submitForm) => {
      const originalStatus = formData.fields.value.status
      fields.status = status
      if (!partyMode.value) fields.customer_name = null
      else fields.party = null
      try { await submitForm() } catch (err) {
        formData.fields.value.status = originalStatus
      }
    }
    formData.fields.value.due_date = formData.today
    formData.fields.value.date = formData.today
    formData.fields.value.is_export = false

    const fetchInvoice = async (fields) => {
      if (!formData?.errors?.value) formData.errors.value = {}
      delete formData.errors.value.fiscal_year
      delete formData.errors.value.invoice_no
      if (
        referenceFormData.value.invoice_no &&
        referenceFormData.value.fiscal_year
      ) {
        if (
          fields.challans &&
          fields.challans.includes(referenceFormData.value.invoice_no)
        ) {
          $q.notify({
            color: 'red-6',
            message: 'Invoice Already Exists!',
            icon: 'report_problem',
            position: 'top-right',
          })
          formData.errors.value.invoice_no = 'The invoice has already been added!'
        } else {
          const url = 'v1/challan/by-voucher-no/'
          useApi(
            url +
            `?invoice_no=${referenceFormData.value.invoice_no}&fiscal_year=${referenceFormData.value.fiscal_year}`
          )
            .then((data) => {
              formData.errors.value = {}
              const response = { ...data }
              if (fields.challans) {
                if (fields.party && fields.party !== response.party || fields.customer_name && fields.customer_name !== response.customer_name) {
                  $q.notify({
                    color: 'red-6',
                    message: 'A single challan can be issued to a single party/customer only',
                    icon: 'report_problem',
                    position: 'top-right',
                  })
                  return
                }
                fields.challans.push(data.id)
              } else fields.challans = [data.id]
              if (fields.challan_numbers) {
                fields.challan_numbers.push(response.voucher_no)
              } else fields.challan_numbers = [response.voucher_no]
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
              if (response.rows && response.rows.length > 0) {
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
        }
      } else {
        $q.notify({
          color: 'red-6',
          message: 'Please fill in the form completely!',
          icon: 'report_problem',
          position: 'top-right',
        })
        if (!formData?.errors?.value) formData.errors.value = {}
        if (!referenceFormData.value.invoice_no) {
          formData.errors.value.invoice_no = 'Invoice Number is required!'
        }
        if (!referenceFormData.value.fiscal_year) {
          formData.errors.value.fiscal_year = 'Fiscal Year is required!'
        }
      }
    }
    const onPartyChange = (value) => {
      let index
      if (!!value && !!formData.formDefaults.value.collections) {
        index =
          formData.formDefaults.value.collections.parties.findIndex(
            (option) => option.id === value
          )
        formData.fields.value.address =
          formData.formDefaults.value.collections.parties[index].address
        if (index) {
          formData.fields.value.mode = 'Credit'
        }
      } else if (!index) formData.fields.value.mode = 'Cash'
    }
    watch(() => formData.formDefaults.value, () => {
      if (formData.formDefaults.value.fields?.hasOwnProperty('trade_discount')) {
        formData.fields.value.trade_discount = formData.formDefaults.value.fields?.trade_discount
      }
      if (formData.isEdit.value) {
        if (formData.fields.value.customer_name) partyMode.value = true
      } else {
        if (formData.formDefaults.value.fields?.mode) {
          if (isNaN(formData.formDefaults.value.fields?.mode)) {
            formData.fields.value.mode = formData.formDefaults.value.fields.mode
          } else {
            formData.fields.value.mode = Number(formData.formDefaults.value.fields.mode)
          }
        } else formData.fields.value.mode = 'Credit'
      }
    })
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
      staticOptions,
      InvoiceTable,
      partyMode,
      switchMode,
      deleteRowErr,
      onSubmitClick,
      importChallanModal,
      referenceFormData,
      fetchInvoice,
      checkPermissions,
      loginStore,
      onPartyChange,
      // TODO: temp
      show_row_column_in_voucher_row,
      discountOptionsComputed
    }
  },
}
</script>
