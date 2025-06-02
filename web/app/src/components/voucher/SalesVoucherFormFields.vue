<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import PartyAlias from 'src/pages/party/PartyAlias.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import SalesDiscountForm from 'src/pages/sales/discount/SalesDiscountForm.vue'
import { useLoginStore } from 'src/stores/login-info'
import { useRoute } from 'vue-router'

const props = defineProps({
  formDefaults: {
    type: Object,
    required: true,
  },
  isEdit: {
    type: Boolean,
    required: false,
  },
  isTemplate: {
    type: Boolean,
    required: false,
  },
  today: {
    type: String,
    required: true,
  },
})

const taxTypes = [
  {
    label: 'No Tax',
    value: 'no_tax',
  },
  {
    label: 'Tax Exclusive',
    value: 'tax_exclusive',
  },
  {
    label: 'Tax Inclusive',
    value: 'tax_inclusive',
  },
]

const route = useRoute()

const importChallanModal = ref(false)

const loginStore = useLoginStore()

const { $q } = useQuasar()

const fields = defineModel('fields')

const errors = defineModel('errors')

if (!props.isEdit) {
  fields.value.due_date = props.today
  fields.value.date = props.today
  fields.value.is_export = false
  fields.value.received_by = ''
}

const customerMode = ref(false)

const aliases = ref([])

watch([customerMode, aliases], () => {
  if (!fields.value.invoice_data) {
    fields.value.invoice_data = {}
  }
  if (!customerMode.value) {
    if (aliases.value.length === 0) {
      fields.value.invoice_data.customer_name = null
    }
  } else {
    fields.value.invoice_data.party = null
  }
})

const referenceFormData = ref({
  invoice_no: null,
  fiscal_year: loginStore.companyInfo.current_fiscal_year_id || null,
})

const fetchInvoice = async (fields) => {
  if (!errors.value) errors.value = {}
  delete errors.value.fiscal_year
  delete errors.value.invoice_no

  if (referenceFormData.value.invoice_no && referenceFormData.value.fiscal_year) {
    if (fields.challans && fields.challans.includes(referenceFormData.value.invoice_no)) {
      $q.notify({
        color: 'red-6',
        message: 'Invoice Already Exists!',
        icon: 'report_problem',
        position: 'top-right',
      })
      errors.value.invoice_no = 'The invoice has already been added!'
    } else {
      const url = `/api/company/${route.params.company}/challan/by-voucher-no/`
      try {
        const data = await useApi(`${url}?invoice_no=${referenceFormData.value.invoice_no}&fiscal_year=${referenceFormData.value.fiscal_year}`)
        errors.value = {}
        const response = { ...data }

        if ((fields.party && fields.party !== response.party) || (fields.customer_name && fields.customer_name !== response.customer_name)) {
          $q.notify({
            color: 'red-6',
            message: 'A single challan can be issued to a single party/customer only',
            icon: 'report_problem',
            position: 'top-right',
          })
          return
        }

        if (fields.challans) {
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
      } catch (err) {
        let message
        if (err.status === 404) {
          message = 'Invoice Not Found!'
        } else {
          message = err.data?.detail || 'Server Error! Please contact us with the problem.'
        }
        $q.notify({
          color: 'red-6',
          message,
          icon: 'report_problem',
          position: 'top-right',
        })
      }
    }
  } else {
    $q.notify({
      color: 'red-6',
      message: 'Please fill in the form completely!',
      icon: 'report_problem',
      position: 'top-right',
    })
    if (!errors.value) errors.value = {}
    if (!referenceFormData.value.invoice_no) {
      errors.value.invoice_no = 'Invoice Number is required!'
    }
    if (!referenceFormData.value.fiscal_year) {
      errors.value.fiscal_year = 'Fiscal Year is required!'
    }
  }
}

const onPartyChange = (obj) => {
  if (obj) {
    fields.value.address = obj.address
    if (obj.aliases && obj.aliases.length > 0) {
      aliases.value = [{ name: obj.name, id: null }, ...obj.aliases.map(item => ({ name: item, id: item }))]
    }
  }
}

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

const staticOptions = {
  discount_types,
  modes,
}

const deleteRowErr = (index, errors, deleteObj) => {
  if (deleteObj) {
    if (!fields.value.deleted_rows) {
      fields.value.deleted_rows = []
    }
    fields.value.deleted_rows.push(deleteObj)
  }
  if (errors && Array.isArray(errors.rows)) {
    errors.rows.splice(index, 1)
  }
}

const modeOptionsComputed = computed(() => {
  const obj = {
    results: [{ id: null, name: 'Credit' }],
    pagination: {},
  }
  if (props.formDefaults?.collections?.payment_modes?.results) {
    obj.results = obj.results.concat(props.formDefaults.collections.payment_modes.results)
    Object.assign(obj.pagination, props.formDefaults.collections.payment_modes.pagination)
  }
  return obj
})

const onPaymentModeChange = (obj) => {
  if (obj && obj.id === null && customerMode.value) {
    $q.notify({
      color: 'orange-4',
      message: 'Can not select credit mode for non-party customer!',
    })
    fields.value.payment_mode = modeOptionsComputed.value.results[1].id
  }
}

watch(
  () => props.formDefaults,
  () => {
    if (props.formDefaults.fields?.hasOwnProperty('trade_discount')) {
      fields.value.trade_discount = props.formDefaults.fields?.trade_discount
    }
    if (props.isEdit) {
      if (fields.value.customer_name) customerMode.value = true
    } else {
      if (props.formDefaults.fields?.payment_mode) {
        fields.value.payment_mode = props.formDefaults.fields.payment_mode
      }
    }
  },
)

fields.value.tax_type = fields.value.tax_type || 'tax_exclusive'
</script>

<template>
  <q-card class="q-mx-lg q-pt-md">
    <q-card-section>
      <div class="row q-col-gutter-md">
        <div v-if="formDefaults.options?.enable_import_challan" class="col-md-6 col-12">
          <q-btn
            color="blue"
            data-testid="import-challan-btn"
            label="Import challan(s)"
            @click="importChallanModal = true"
          />
          <div v-if="fields.challans && fields.challans.length > 0">
            <q-input
              v-model="fields.challan_numbers"
              dense
              disable
              label="Import challan(s)"
            />
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
                  autofocus
                  data-testid="challan-no-input"
                  label="Challan No.*"
                  type="number"
                  :error="errors?.invoice_no ?? null"
                  :error-message="errors?.invoice_no"
                />
                <q-select
                  v-model="referenceFormData.fiscal_year"
                  emit-value
                  map-options
                  class="q-mt-md"
                  data-testid="fiscal-year-select"
                  label="Fiscal Year"
                  option-label="name"
                  option-value="id"
                  :error="errors?.fiscal_year ?? null"
                  :error-message="errors?.fiscal_year"
                  :options="formDefaults.options?.fiscal_years"
                />
                <div class="row justify-end q-mt-lg">
                  <q-btn
                    color="green"
                    data-testid="add-reference-btn"
                    label="Add"
                    size="md"
                    @click="fetchInvoice(fields)"
                  />
                </div>
              </q-card-section>
            </q-card>
          </q-dialog>
        </div>
        <div class="col-md-6 col-12">
          <div class="row">
            <div class="col-10">
              <q-input
                v-if="customerMode"
                v-model="fields.customer_name"
                data-testid="customer-name-input"
                label="Customer Name"
                :error="errors?.customer_name ?? null"
                :error-message="errors?.customer_name"
              />
              <n-auto-complete-v2
                v-else
                v-model="fields.party"
                label="Party"
                :emit-obj="true"
                :endpoint="`/api/company/${$route.params.company}/sales-voucher/create-defaults/parties`"
                :error="errors?.party ? errors?.party : null"
                :modal-component="checkPermissions('party.create') ? PartyForm : null"
                :options="formDefaults.collections?.parties"
                :static-option="fields.selected_party_obj"
                @update-obj="onPartyChange"
              />
            </div>

            <div class="col-2 row justify-center q-py-md">
              <q-btn
                flat
                data-testid="switch-account-group-btn"
                size="md"
                @click="() => switchMode(fields)"
              >
                <q-icon name="mdi-account-group" />
              </q-btn>
            </div>
          </div>
          <div>
            <n-auto-complete
              v-if="!customerMode && fields.party && aliases.length > 0"
              v-model="fields.customer_name"
              class="col-md-6 col-12"
              data-testid="alias-select"
              label="Name on Invoice"
              :error="errors?.customer_name ? errors?.customer_name : null"
              :modal-component="checkPermissions('partyalias.create') ? PartyAlias : null"
              :options="aliases"
            />
          </div>
        </div>

        <template v-if="!isTemplate">
          <date-picker
            v-if="formDefaults.options?.enable_sales_date_edit"
            v-model="fields.date"
            class="col-md-6 col-12"
            label="Invoice Date*"
            :error="errors?.date ? errors?.date : null"
            :error-message="errors?.date"
          />
          <DateInputDisabled
            v-else
            class="col-md-6 col-12"
            label="Invoice Date*"
            :date="fields.date"
          />
        </template>
        <q-input
          v-model="fields.address"
          class="col-md-6 col-12"
          data-testid="address-input"
          label="Address"
          :error="!!errors?.address"
          :error-message="errors?.address"
        />
        <date-picker
          v-if="formDefaults.options?.enable_due_date_in_voucher && !isTemplate"
          v-model="fields.due_date"
          class="col-md-6 col-12"
          data-testid="due-date"
          label="Due Date"
          :error="errors?.due_date ? errors.due_date : null"
          :error-message="errors?.due_date"
          :to-limit="fields.date"
        />
        <div
          v-if="formDefaults.options?.enable_discount_in_voucher && !isTemplate"
          class="col-md-6 col-12 row q-col-gutter-md"
        >
          <div data-testid="overall-discount-type-div" :class="['Percent', 'Amount'].includes(fields.discount_type) ? 'col-6' : 'col-12'">
            <n-auto-complete
              v-model="fields.discount_type"
              label="Discount"
              :error="errors?.discount_type ? errors?.discount_type : null"
              :modal-component="checkPermissions('salesdiscount.create') ? SalesDiscountForm : null"
              :options="staticOptions.discount_types.concat(formDefaults.collections?.discounts)"
            />
          </div>
          <div class="col-6 row">
            <div v-if="fields.discount_type === 'Amount' || fields.discount_type === 'Percent'" :class="formDefaults.options?.show_trade_discount_in_voucher ? 'col-6' : 'col-12'">
              <q-input
                v-model.number="fields.discount"
                class="col-6"
                data-testid="discount-input"
                label="Discount"
                :error="!!errors?.discount"
                :error-message="errors?.discount"
              />
            </div>
            <div v-if="formDefaults.options?.show_trade_discount_in_voucher && ['Percent', 'Amount'].includes(fields.discount_type)" class="col-3 row">
              <q-checkbox v-model="fields.trade_discount" data-testid="trade-discount-input" label="Trade Discount?" />
            </div>
          </div>
        </div>
        <div class="col-12 col-md-6">
          <n-auto-complete-v2
            v-model="fields.payment_mode"
            data-testid="payment-mode-select"
            label="Payment Mode *"
            :emit-obj="true"
            :endpoint="`/api/company/${$route.params.company}/sales-voucher/create-defaults/payment_modes`"
            :error="errors?.payment_mode ? errors?.payment_mode : null"
            :map-options="true"
            :options="modeOptionsComputed"
            :static-option="isEdit ? fields.selected_payment_mode_obj : formDefaults.options?.default_payment_mode_obj"
            @update-obj="onPaymentModeChange"
          >
            <template #append>
              <q-icon
                v-if="fields.payment_mode !== null"
                class="cursor-pointer"
                name="clear"
                @click.stop.prevent="fields.payment_mode = null"
              />
            </template>
          </n-auto-complete-v2>
        </div>
        <div class="col-12 col-md-6">
          <q-select
            v-model="fields.tax_type"
            emit-value
            map-options
            class="w-full"
            label="Tax Type"
            option-label="label"
            option-value="value"
            :options="taxTypes"
          />
        </div>
        <div
          v-if="
            formDefaults.options?.enable_reference_in_voucher
              && !isTemplate"
          class="col-12 col-md-6"
        >
          <q-input
            v-model="fields.reference"
            autogrow
            class="col-12 col-md-10"
            data-testid="reference-input"
            label="Reference"
            type="textarea"
            :error="!!errors?.reference"
            :error-message="errors?.reference"
          />
        </div>
      </div>
    </q-card-section>
  </q-card>
  <invoice-table
    v-if="formDefaults.collections"
    v-model="fields.rows"
    used-in="sales"
    :discount-options="staticOptions.discount_types.concat(formDefaults.collections?.discounts)"
    :enable-row-description="formDefaults.options?.enable_row_description"
    :errors="errors?.rows ? errors.rows : null"
    :has-challan="!!(fields.challans && fields.challans.length > 0)"
    :input-amount="formDefaults.options?.enable_amount_entry"
    :is-fifo="formDefaults.options?.enable_fifo"
    :item-options="formDefaults.collections ? formDefaults.collections.items : null"
    :main-discount="{
      discount_type: fields.discount_type,
      discount: fields.discount,
    }"
    :missing-fields-config="{
      enabled: true,
      fields: {
        code: formDefaults?.fields?.require_item_code,
        hs_code: formDefaults?.fields?.require_item_hs_code,
      },
    }"
    :show-rate-quantity="formDefaults.options?.show_rate_quantity_in_voucher"
    :show-row-trade-discount="formDefaults.options?.show_trade_discount_in_row"
    :tax-options="formDefaults.collections?.tax_schemes"
    :tax-type="fields.tax_type"
    :unit-options="formDefaults.collections ? formDefaults.collections.units : null"
    @delete-row-err="deleteRowErr"
  />
  <div class="row q-px-lg">
    <div class="col-12 col-md-4 row">
      <q-input
        v-model="fields.remarks"
        autogrow
        class="col-12 col-md-10"
        data-testid="remarks-input"
        label="Remarks"
        type="textarea"
        :error="!!errors?.remarks"
        :error-message="errors?.remarks"
      />
    </div>

    <div class="col-12 col-md-4 row">
      <n-auto-complete-v2
        v-if="loginStore.companyInfo.enable_sales_agents"
        v-model="fields.sales_agent"
        class="col-12"
        data-testid="sales-agent-select"
        label="Sales Agent"
        :endpoint="`/api/company/${$route.params.company}/sales-voucher/create-defaults/sales_agents`"
        :error="errors?.sales_agent"
        :options="formDefaults.collections?.sales_agents"
        :static-option="fields.selected_sales_agent_obj"
      />
    </div>
    <div class="col-12 col-md-1 row"></div>
    <div class="col-12 col-md-3 row">
      <q-checkbox
        v-model="fields.is_export"
        data-testid="export-checkbox"
        label="Export?"
      />
    </div>
    <div class="col-md-12">
      <q-label class="q-mb-lg">
        Received By
      </q-label>
      <q-editor v-model="fields.received_by" />
    </div>
  </div>
</template>
