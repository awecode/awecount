<script>
import InvoiceTable from 'src/components/voucher/InvoiceTable.vue'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import CategoryForm from 'src/pages/account/category/CategoryForm.vue'
import PartyAlias from 'src/pages/party/PartyAlias.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import SalesDiscountForm from 'src/pages/sales/discount/SalesDiscountForm.vue'
import { useLoginStore } from 'src/stores/login-info.js'

export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/sales-voucher/`
    const loginStore = useLoginStore()
    const show_row_column_in_voucher_row = true
    // TODO: temp
    const $q = useQuasar()
    const importChallanModal = ref(false)
    const referenceFormData = ref({
      invoice_no: null,
      fiscal_year: loginStore.companyInfo.current_fiscal_year_id || null,
    })
    const staticOptions = {
      discount_types,
      modes,
    }
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/sales-voucher/list/',
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Sales Invoice Update' : 'Sales Invoice Add'} | Awecount`,
      }
    })

    const customerMode = ref(false)
    const switchMode = (fields) => {
      if (fields.payment_mode === null && !customerMode.value) {
        $q.notify({
          color: 'orange-4',
          message: 'Credit customer must be a party!',
        })
        return
      }

      customerMode.value = !customerMode.value
    }
    const deleteRowErr = (index, errors, deleteObj) => {
      if (deleteObj) {
        if (!formData.fields.value.deleted_rows) {
          formData.fields.value.deleted_rows = []
        }
        formData.fields.value.deleted_rows.push(deleteObj)
      }
      if (errors && Array.isArray(errors.rows)) {
        errors.rows.splice(index, 1)
      }
    }
    const onSubmitClick = async (status) => {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      if (!customerMode.value) {
        if (aliases.value.length === 0) {
          formData.fields.value.customer_name = null
        }
      } else {
        formData.fields.value.party = null
      }
      const data = await formData.submitForm()
      if (data && data.hasOwnProperty('error')) {
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
      if (referenceFormData.value.invoice_no && referenceFormData.value.fiscal_year) {
        if (fields.challans && fields.challans.includes(referenceFormData.value.invoice_no)) {
          $q.notify({
            color: 'red-6',
            message: 'Invoice Already Exists!',
            icon: 'report_problem',
            position: 'top-right',
          })
          formData.errors.value.invoice_no = 'The invoice has already been added!'
        } else {
          const url = 'v1/challan/by-voucher-no/'
          useApi(`${url}?invoice_no=${referenceFormData.value.invoice_no}&fiscal_year=${referenceFormData.value.fiscal_year}`)
            .then((data) => {
              formData.errors.value = {}
              const response = { ...data }
              if (fields.challans) {
                if ((fields.party && fields.party !== response.party) || (fields.customer_name && fields.customer_name !== response.customer_name)) {
                  $q.notify({
                    color: 'red-6',
                    message: 'A single challan can be issued to a single party/customer only',
                    icon: 'report_problem',
                    position: 'top-right',
                  })
                  return
                }
                fields.challans.push(data.id)
              } else {
                fields.challans = [data.id]
              }
              if (fields.challan_numbers) {
                fields.challan_numbers.push(response.voucher_no)
              } else {
                fields.challan_numbers = [response.voucher_no]
              }
              const removeArr = ['id', 'date', 'voucher_meta', 'print_count', 'issue_datetime', 'is_export', 'status', 'due_date', 'rows', 'date', 'remarks']
              if (data.customer_name) {
                customerMode.value = true
              }
              if (data.party) {
                customerMode.value = false
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
                message,
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

    const aliases = ref([])
    const onPartyChange = (obj) => {
      if (obj) {
        formData.fields.value.address = obj.address
        if (obj.aliases && obj.aliases.length > 0) {
          aliases.value = [{ name: obj.name, id: null }, ...obj.aliases.map((item) => ({ name: item, id: item }))]
        }
      }
    }

    watch(
      () => formData.formDefaults.value,
      () => {
        if (formData.formDefaults.value.fields?.hasOwnProperty('trade_discount')) {
          formData.fields.value.trade_discount = formData.formDefaults.value.fields?.trade_discount
        }
        if (formData.isEdit.value) {
          if (formData.fields.value.customer_name) customerMode.value = true
        } else {
          if (formData.formDefaults.value.fields?.payment_mode) {
            formData.fields.value.payment_mode = formData.formDefaults.value.fields.payment_mode
          }
        }
      },
    )

    const modeOptionsComputed = computed(() => {
      const obj = {
        results: [{ id: null, name: 'Credit' }],
        pagination: {},
      }
      if (formData?.formDefaults.value?.collections?.payment_modes?.results) {
        obj.results = obj.results.concat(formData.formDefaults.value.collections.payment_modes.results)
        Object.assign(obj.pagination, formData.formDefaults.value.collections.payment_modes.pagination)
      }
      return obj
    })

    const onPaymentModeChange = (obj) => {
      // if customer is not party then credit mode can not be selected
      if (obj && obj.id === null && customerMode.value) {
        $q.notify({
          color: 'orange-4',
          message: 'Can not select credit mode for non-party customer!',
        })
        formData.fields.value.payment_mode = modeOptionsComputed.value.results[1].id
      }
    }

    return {
      ...formData,
      CategoryForm,
      PartyForm,
      PartyAlias,
      SalesDiscountForm,
      staticOptions,
      InvoiceTable,
      customerMode,
      switchMode,
      deleteRowErr,
      onSubmitClick,
      importChallanModal,
      referenceFormData,
      fetchInvoice,
      checkPermissions,
      loginStore,
      aliases,
      onPartyChange,
      // TODO: temp
      show_row_column_in_voucher_row,
      modeOptionsComputed,
      onPaymentModeChange,
    }
  },
}
</script>

<template>
  <q-form v-if="fields" class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6" data-testid="form-title">
          <span v-if="!isEdit">New Sales Invoice | Draft</span>
          <span v-else>
            Update Sale Invoice | {{ fields.status }}
            <span v-if="fields.voucher_no">| # {{ fields.voucher_no }}</span>
          </span>
        </div>
      </q-card-section>
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div v-if="formDefaults.options?.enable_import_challan" class="col-md-6 col-12">
              <q-btn color="blue" data-testid="import-challan-btn" label="Import challan(s)" @click="importChallanModal = true" />
              <div v-if="fields.challans && fields.challans.length > 0">
                <q-input v-model="fields.challan_numbers" dense disable label="Import challan(s)" />
              </div>
              <q-dialog v-model="importChallanModal" @before-hide="errors && delete errors?.fiscal_year && delete errors?.invoice_no">
                <q-card style="min-width: min(60vw, 400px)">
                  <q-card-section class="bg-grey-4">
                    <div class="text-h6">
                      <span>Add Reference Challan(s)</span>
                    </div>
                  </q-card-section>

                  <q-card-section class="q-mx-lg">
                    <q-input v-model.number="referenceFormData.invoice_no" label="Challan No.*" autofocus type="number" :error="!!errors?.invoice_no" :error-message="errors?.invoice_no" data-testid="challan-no-input" />
                    <q-select v-model="referenceFormData.fiscal_year" class="q-mt-md" label="Fiscal Year" :options="formDefaults.options?.fiscal_years" option-value="id" option-label="name" map-options emit-value data-testid="fiscal-year-select" :error="!!errors?.fiscal_year" :error-message="errors?.fiscal_year" />
                    <div class="row justify-end q-mt-lg">
                      <q-btn color="green" label="Add" size="md" data-testid="add-reference-btn" @click="fetchInvoice(fields)" />
                    </div>
                  </q-card-section>
                </q-card>
              </q-dialog>
            </div>
            <div class="col-md-6 col-12">
              <div class="row">
                <div class="col-10">
                  <q-input v-if="customerMode" v-model="fields.customer_name" label="Customer Name" :error-message="errors?.customer_name" :error="!!errors?.customer_name" data-testid="customer-name-input" />
                  <n-auto-complete-v2 v-else v-model="fields.party" :options="formDefaults.collections?.parties" label="Party" :error="errors?.party ? errors?.party : null" :modal-component="checkPermissions('party.create') ? PartyForm : null" :static-option="fields.selected_party_obj" :endpoint="`/api/company/${$route.params.company}/sales-voucher/create-defaults/parties`" :emit-obj="true" @update-obj="onPartyChange" />
                </div>

                <div class="col-2 row justify-center q-py-md">
                  <q-btn flat size="md" data-testid="switch-account-group-btn" @click="() => switchMode(fields)">
                    <q-icon name="mdi-account-group" />
                  </q-btn>
                </div>
              </div>
              <div>
                <n-auto-complete v-if="!customerMode && fields.party && aliases.length > 0" v-model="fields.customer_name" class="col-md-6 col-12" label="Name on Invoice" :options="aliases" :modal-component="checkPermissions('partyalias.create') ? PartyAlias : null" :error="errors?.customer_name ? errors?.customer_name : null" data-testid="alias-select" />
              </div>
            </div>

            <date-picker v-if="formDefaults.options?.enable_sales_date_edit" v-model="fields.date" label="Invoice Date*" class="col-md-6 col-12" :error="!!errors?.date" :error-message="errors?.date" />
            <DateInputDisabled v-else :date="fields.date" class="col-md-6 col-12" label="Invoice Date*" />
            <q-input v-model="fields.address" class="col-md-6 col-12" label="Address" :error-message="errors?.address" :error="!!errors?.address" data-testid="address-input" />
            <date-picker v-if="formDefaults.options?.enable_due_date_in_voucher" v-model="fields.due_date" label="Due Date" class="col-md-6 col-12" :error="!!errors?.due_date" :error-message="errors?.due_date" :to-limit="fields.date" data-testid="due-date" />
            <div class="col-md-6 col-12 row q-col-gutter-md">
              <div :class="['Percent', 'Amount'].includes(fields.discount_type) ? 'col-6' : 'col-12'" data-testid="overall-discount-type-div">
                <n-auto-complete v-model="fields.discount_type" label="Discount" :error="errors?.discount_type ? errors?.discount_type : null" :options="staticOptions.discount_types.concat(formDefaults.collections?.discounts)" :modal-component="checkPermissions('salesdiscount.create') ? SalesDiscountForm : null" />
              </div>
              <div class="col-6 row">
                <div v-if="fields.discount_type === 'Amount' || fields.discount_type === 'Percent'" :class="formDefaults.options?.show_trade_discount_in_voucher ? 'col-6' : 'col-12'">
                  <q-input v-model.number="fields.discount" class="col-6" label="Discount" :error-message="errors?.discount" :error="!!errors?.discount" data-testid="discount-input" />
                </div>
                <div v-if="formDefaults.options?.show_trade_discount_in_voucher && ['Percent', 'Amount'].includes(fields.discount_type)" class="col-3 row">
                  <q-checkbox v-model="fields.trade_discount" label="Trade Discount?" data-testid="trade-discount-input" />
                </div>
              </div>
            </div>
          </div>
          <!-- <div class="row q-col-gutter-md"></div> -->
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete-v2 v-model="fields.payment_mode" label="Payment Mode *" :endpoint="`/api/company/${$route.params.company}/sales-voucher/create-defaults/payment_modes`" :error="!!errors?.payment_mode" :options="modeOptionsComputed" :static-option="isEdit ? fields.selected_payment_mode_obj : formDefaults.options?.default_payment_mode_obj" data-testid="payment-mode-select" :emit-obj="true" :map-options="true" @update-obj="onPaymentModeChange">
                <template #append>
                  <q-icon v-if="fields.payment_mode !== null" class="cursor-pointer" name="clear" @click.stop.prevent="fields.payment_mode = null" />
                </template>
              </n-auto-complete-v2>
            </div>
          </div>
        </q-card-section>
      </q-card>
      <invoice-table
        v-if="formDefaults.collections"
        v-model="fields.rows"
        :item-options="formDefaults.collections ? formDefaults.collections.items : null"
        :unit-options="formDefaults.collections ? formDefaults.collections.units : null"
        :discount-options="staticOptions.discount_types.concat(formDefaults.collections?.discounts)"
        :tax-options="formDefaults.collections?.tax_schemes"
        :main-discount="{
          discount_type: fields.discount_type,
          discount: fields.discount,
        }"
        :errors="!!errors?.rows ? errors.rows : null"
        :enable-row-description="formDefaults.options?.enable_row_description"
        :show-row-trade-discount="formDefaults.options?.show_trade_discount_in_row"
        :input-amount="formDefaults.options?.enable_amount_entry"
        :show-rate-quantity="formDefaults.options?.show_rate_quantity_in_voucher"
        :is-fifo="formDefaults.options?.enable_fifo"
        used-in="sales"
        :has-challan="!!(fields.challans && fields.challans.length > 0)"
        @delete-row-err="(index, deleteObj) => deleteRowErr(index, errors, deleteObj)"
      />
      <div class="row q-px-lg">
        <div class="col-12 col-md-6 row">
          <!-- <q-input
            v-model="fields.remarks"
            label="Remarks"
            type="textarea"
          ></q-input> -->
          <q-input v-model="fields.remarks" label="Remarks" type="textarea" autogrow class="col-12 col-md-10" :error="!!errors?.remarks" :error-message="errors?.remarks" data-testid="remarks-input" />
        </div>
        <div class="col-12 col-md-6 row justify-between">
          <div class="col-3">
            <q-checkbox v-model="fields.is_export" label="Export?" class="q-mt-md col-3" data-testid="export-checkbox" />
          </div>
          <div class="col-9">
            <n-auto-complete-v2 v-if="loginStore.companyInfo.enable_sales_agents" v-model="fields.sales_agent" label="Sales Agent" class="col-8" :error="!!errors?.sales_agent" :options="formDefaults.collections?.sales_agents" :endpoint="`/api/company/${$route.params.company}/sales-voucher/create-defaults/sales_agents`" :static-option="fields.selected_sales_agent_obj" data-testid="sales-agent-select" />
          </div>
          <!-- TODO: add sales agent form -->
        </div>
      </div>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn v-if="!isEdit && checkPermissions('sales.create')" :loading="loading" color="orange-8" label="Save Draft" type="submit" data-testid="issue-btn" @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" />
        <q-btn v-if="isEdit && fields.status === 'Draft' && checkPermissions('sales.modify')" :loading="loading" color="orange-8" :label="isEdit ? 'Update Draft' : 'Save Draft'" type="submit" data-testid="draft-btn" @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" />
        <q-btn
          v-if="checkPermissions('sales.create')"
          :loading="loading"
          color="green"
          :label="
            isEdit ?
              fields?.status === 'Issued' ? 'Update'
              : fields?.status === 'Draft' ? `Issue # ${formDefaults.options?.voucher_no || 1} from Draft`
              : 'update'
            : `Issue # ${formDefaults.options?.voucher_no || 1}`
          "
          data-testid="create/update-btn"
          @click.prevent="
            () =>
              onSubmitClick(
                isEdit ?
                  fields.status === 'Draft' ?
                    'Issued'
                  : fields.status
                : 'Issued',
              )
          "
        />
      </div>
    </q-card>
  </q-form>
</template>
