<script setup>
import Decimal from 'decimal.js'
import FormattedNumber from 'src/components/FormattedNumber.vue'
import checkPermissions from 'src/composables/checkPermissions'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import PartyForm from 'src/pages/party/PartyForm.vue'
import PurchaseDiscountForm from 'src/pages/purchase/discounts/PurchaseDiscountForm.vue'
import { useLoginStore } from 'src/stores/login-info'
import { useRoute } from 'vue-router'
import InvoiceTable from './InvoiceTable.vue'

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

const loginStore = useLoginStore()
const route = useRoute()
const staticOptions = {
  discount_types,
  modes,
}

// Currency conversion matrix for USD, INR, and NPR
const EXCHANGE_RATES = {
  USD: {
    INR: '83.12',
    NPR: '135.76',
  },
  INR: {
    USD: '0.012',
    NPR: '1.60',
  },
  NPR: {
    USD: '0.0075',
    INR: '0.62',
  },
}

// Available currencies
const AVAILABLE_CURRENCIES = ['USD', 'INR', 'NPR']

// Utility function to convert currency
const convertCurrency = (amount, fromCurrency, toCurrency) => {
  if (!amount) return new Decimal(0)

  amount = new Decimal(amount)

  if (fromCurrency === toCurrency) return amount

  // Get exchange rate
  const rate = new Decimal(EXCHANGE_RATES[fromCurrency]?.[toCurrency] || '0')
  if (!rate) {
    console.warn(`Exchange rate not found for ${fromCurrency} to ${toCurrency}`)
    return amount
  }

  return amount.mul(rate)
}

const fields = defineModel('fields')

const showLandedCosts = ref(false)

// Initialize landed costs if not present
if (!fields.value.landed_cost_rows) {
  fields.value.landed_cost_rows = []
}
const landedCostTypes = [
  { label: 'Duty', value: 'Duty' },
  { label: 'Labor', value: 'Labor' },
  { label: 'Freight', value: 'Freight' },
  { label: 'Insurance', value: 'Insurance' },
  { label: 'Brokerage', value: 'Brokerage' },
  { label: 'Storage', value: 'Storage' },
  { label: 'Packaging', value: 'Packaging' },
  { label: 'Loading', value: 'Loading' },
  { label: 'Unloading', value: 'Unloading' },
  { label: 'Regulatory Fee', value: 'Regulatory Fee' },
  { label: 'Customs Declaration', value: 'Customs Declaration' },
  { label: 'Other Charges', value: 'Other Charges' },
]

// Presets for landed cost types
const LANDED_COST_PRESETS = {
  'Duty': {
    is_percentage: true,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
  'Freight': {
    is_percentage: false,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
  'Brokerage': {
    is_percentage: false,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
  'Insurance': {
    is_percentage: false,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
  'Storage': {
    is_percentage: false,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
  'Labor': {
    is_percentage: false,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
  'Regulatory Fee': {
    is_percentage: false,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
  'Customs Declaration': {
    is_percentage: false,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
  'Packaging': {
    is_percentage: false,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
  'Loading': {
    is_percentage: false,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
  'Unloading': {
    is_percentage: false,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
  'Other Charges': {
    is_percentage: false,
    default_currency: loginStore.companyInfo.currency_code || 'USD',
  },
}

const landedCostColumns = [
  {
    name: 'type',
    label: 'Cost Type',
    field: 'type',
    align: 'left',
    sortable: true,
    style: 'width: 150px',
  },
  {
    name: 'is_percentage',
    label: 'Amount Type',
    field: 'is_percentage',
    align: 'center',
    style: 'width: 120px',
  },
  {
    name: 'currency',
    label: 'Currency',
    field: 'currency',
    align: 'center',
    style: 'width: 100px',
  },
  {
    name: 'amount',
    label: 'Amount',
    field: 'amount',
    align: 'right',
    sortable: true,
    style: 'width: 200px',
  },
  {
    name: 'tax_scheme',
    label: 'Tax Scheme',
    field: 'tax_scheme',
    align: 'left',
    style: 'width: 150px',
  },
  {
    name: 'credit_account',
    label: 'Credit Account',
    field: 'credit_account',
    align: 'left',
    style: 'width: 150px',
  },
  {
    name: 'description',
    label: 'Description',
    field: 'description',
    align: 'left',
    sortable: true,
    style: 'width: 200px',
  },
  {
    name: 'actions',
    label: 'Actions',
    field: 'actions',
    align: 'center',
    style: 'width: 80px',
  },
]

const addLandedCostRow = () => {
  if (!fields.value.landed_cost_rows) {
    fields.value.landed_cost_rows = []
  }
  fields.value.landed_cost_rows.push({
    type: '',
    value: 0,
    amount: 0,
    description: '',
    is_percentage: false,
    currency: loginStore.companyInfo.currency_code || 'USD',
    tax_scheme: null,
    credit_account: null,
  })
}

// Handle type selection to apply presets
const handleTypeChange = (row) => {
  if (row.type && LANDED_COST_PRESETS[row.type]) {
    const preset = LANDED_COST_PRESETS[row.type]
    row.is_percentage = preset.is_percentage
    row.currency = preset.default_currency
  }
}

// Function to convert percentage amounts to fixed amounts based on invoice total
const convertPercentagesToFixedAmounts = () => {
  if (!fields.value.landed_cost_rows) return

  // Calculate invoice total (sum of all row amounts)
  const invoiceTotal = fields.value.rows?.reduce((sum, row) => sum.add(new Decimal(row.rate || '0').mul(row.quantity || '0')), new Decimal('0')) || new Decimal('0')

  const targetCurrency = loginStore.companyInfo.currency_code || 'USD'

  fields.value.landed_cost_rows.forEach((row) => {
    if (row.is_percentage && row.value) {
      // For percentage-based costs, just calculate the amount without currency conversion
      row.amount = invoiceTotal.mul(row.value).div('100')
    } else {
      // For fixed amounts, convert to target currency if needed
      row.amount = convertCurrency(row.value, row.currency, targetCurrency)
    }
  })
}

const averageRate = computed(() => {
  if (!fields.value.rows || !fields.value.landed_cost_rows) return 0
  const totalAmount = fields.value.rows.reduce((sum, row) => sum.add(new Decimal(row.rate || '0').mul(row.quantity || '0')), new Decimal('0'))
  const totalLandedCosts = fields.value.landed_cost_rows.reduce((sum, row) => sum.add(row.amount || '0'), new Decimal('0'))
  const totalQuantity = fields.value.rows.reduce((sum, row) => sum.add(row.quantity || '0'), new Decimal('0'))
  return totalAmount.add(totalLandedCosts).div(totalQuantity).toNumber()
})

// Watch for initial data to copy amount to value
watch(
  () => fields.value.landed_cost_rows,
  (newRows) => {
    if (newRows?.length) {
      newRows.forEach((row) => {
        if (row.amount && !row.value) {
          row.value = row.amount
          row.is_percentage = false
          row.currency = loginStore.companyInfo.currency_code || 'USD'
        }
      })
      showLandedCosts.value = true
    }
  },
  { immediate: true },
)

// Watch for changes in rows to update fixed amounts
watch(
  () => fields.value.rows,
  () => {
    // Only update if there are landed cost rows with percentage values
    if (fields.value.landed_cost_rows?.some(row => row.is_percentage && row.value)) {
      convertPercentagesToFixedAmounts()
    }
  },
  { deep: true },
)

// Watch for changes in landed cost rows to update fixed amounts
watch(
  () => fields.value.landed_cost_rows?.map(row => ({
    is_percentage: row.is_percentage,
    value: row.value,
    currency: row.currency,
  })),
  () => {
    convertPercentagesToFixedAmounts()
  },
  { deep: true },
)

const removeLandedCostRow = (index) => {
  fields.value.landed_cost_rows.splice(index, 1)
}

const errors = defineModel('errors')

if (!props.isEdit) {
  fields.value.date = props.today
  fields.value.due_date = props.today
  fields.value.is_import = false
}

const importPurchaseOrder = ref(false)

const referenceFormData = ref({
  invoice_no: null,
  fiscal_year: loginStore.companyInfo.current_fiscal_year_id || null,
})

const fetchInvoice = async (data) => {
  if (!errors?.value) errors.value = {}
  delete errors.value.fiscal_year
  delete errors.value.invoice_no
  const fetchData = data || { invoice_no: referenceFormData.value.invoice_no, fiscal_year: referenceFormData.value.fiscal_year }
  if (fetchData.invoice_no && fetchData.fiscal_year) {
    if (fields.value.purchase_orders && fields.value.purchase_orders.includes(fetchData.invoice_no)) {
      $q.notify({
        color: 'red-6',
        message: 'Invoice Already Exists!',
        icon: 'report_problem',
        position: 'top-right',
      })
      errors.value.invoice_no = 'The invoice has already been added!'
    } else {
      const url = `/api/company/${route.params.company}/purchase-order/by-voucher-no/`
      useApi(`${url}?invoice_no=${fetchData.invoice_no}&fiscal_year=${fetchData.fiscal_year}`)
        .then((data) => {
          const response = { ...data }
          if (fields.value.purchase_orders) {
            if (fields.value.party && fields.value.party !== response.party) {
              $q.notify({
                color: 'red-6',
                message: 'A single purchase order can be issued to a single party only',
                icon: 'report_problem',
                position: 'top-right',
              })
              return
            }
            fields.value.purchase_orders.push(data.id)
          } else {
            fields.value.purchase_orders = [data.id]
          }
          if (fields.value.purchase_order_numbers) {
            fields.value.purchase_order_numbers.push(response.voucher_no)
          } else {
            fields.value.purchase_order_numbers = [response.voucher_no]
          }
          const removeArr = ['id', 'date', 'voucher_meta', 'print_count', 'issue_datetime', 'is_export', 'status', 'due_date', 'rows', 'date', 'remarks', 'voucher_no']
          removeArr.forEach((item) => {
            delete data[item]
          })
          for (const key in data) {
            fields.value[key] = data[key]
            // if (key === )
          }
          if (response.rows && response.rows.length > 0) {
            if (!fields.value.rows) fields.value.rows = []
            response.rows.forEach((row) => {
              delete row.id
              fields.value.rows.push(row)
            })
          }
          // if (data.discount_obj && data.discount_obj.id) {
          //   fields.discount_type = data.discount_obj.id
          // }
          importPurchaseOrder.value = false
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
    if (!errors?.value) errors.value = {}
    if (!referenceFormData.value.invoice_no) {
      errors.value.invoice_no = 'Invoice Number is required!'
    }
    if (!referenceFormData.value.fiscal_year) {
      errors.value.fiscal_year = 'Fiscal Year is required!'
    }
  }
}

const discountOptionsComputed = computed(() => {
  if (props.formDefaults?.collections?.discounts) {
    return staticOptions.discount_types.concat(props.formDefaults.collections.discounts)
  } else {
    return staticOptions.discount_types
  }
})

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

const deleteRowErr = (index, errors, deleteObj) => {
  if (deleteObj) {
    if (!fields.value.deleted_rows) {
      fields.value.deleted_rows = []
    }
    fields.value.deleted_rows.push(deleteObj)
  }
  if (errors.rows) errors.rows.splice(index, 1)
}

watch(
  () => props.formDefaults,
  () => {
    if (!props.isEdit) {
      if (props.formDefaults.fields?.mode) {
        if (Number.isNaN(props.formDefaults.fields?.mode)) {
          fields.value.mode = props.formDefaults.fields.mode
        } else {
          fields.value.mode = Number(props.formDefaults.fields.mode)
        }
      } else {
        fields.value.mode = 'Credit'
      }
    }

    if (Object.hasOwn(props.formDefaults.fields, 'trade_discount')) {
      fields.value.trade_discount = props.formDefaults.fields?.trade_discount
    }
  },
)

onMounted(() => {
  const route = useRoute()
  if (route.query.purchase_order && route.query.fiscal_year) {
    const data = { invoice_no: route.query.purchase_order, fiscal_year: route.query.fiscal_year }
    fetchInvoice(data)
  }
})
</script>

<template>
  <q-card class="q-mx-lg q-pt-md">
    <q-card-section>
      <div class="row q-col-gutter-md">
        <div v-if="formDefaults.options?.enable_purchase_order_import" class="col-md-6 col-12">
          <q-btn color="blue" label="Import purchase order(s)" @click="importPurchaseOrder = true" />
          <div v-if="fields.purchase_orders && fields.purchase_orders.length > 0">
            <q-input
              v-model="fields.purchase_order_numbers"
              dense
              disable
              label="Purchase Order(s)"
            />
          </div>
          <q-dialog v-model="importPurchaseOrder">
            <q-card style="min-width: min(60vw, 400px)">
              <q-card-section class="bg-grey-4 flex justify-between">
                <div class="text-h6">
                  <span>Add Reference Purchase Order(s)</span>
                </div>
                <q-btn
                  v-close-popup
                  dense
                  flat
                  round
                  class="text-white bg-red-500 opacity-95"
                  icon="close"
                />
              </q-card-section>

              <q-card-section class="q-mx-lg">
                <q-input
                  v-model.number="referenceFormData.invoice_no"
                  autofocus
                  label="Purchase Order No.*"
                  type="number"
                  :error="!!errors?.invoice_no"
                  :error-message="errors?.invoice_no"
                />
                <q-select
                  v-model="referenceFormData.fiscal_year"
                  emit-value
                  map-options
                  class="q-mt-md"
                  label="Fiscal Year"
                  option-label="name"
                  option-value="id"
                  :error="!!errors?.fiscal_year"
                  :error-message="errors?.fiscal_year"
                  :options="formDefaults.options?.fiscal_years"
                />
                <div class="row justify-end q-mt-lg">
                  <q-btn
                    color="green"
                    label="Add"
                    size="md"
                    @click="fetchInvoice()"
                  />
                </div>
              </q-card-section>
            </q-card>
          </q-dialog>
        </div>
        <div class="col-md-6 col-12">
          <n-auto-complete-v2
            v-model="fields.party"
            label="Party"
            :endpoint="`/api/company/${$route.params.company}/sales-voucher/create-defaults/parties`"
            :error="errors?.party ? errors?.party : ''"
            :modal-component="checkPermissions('party.create') ? PartyForm : null"
            :options="formDefaults.collections?.parties"
            :static-option="fields.selected_party_obj"
          />
        </div>
        <q-input
          v-if="!isTemplate"
          v-model="fields.voucher_no"
          class="col-md-6 col-12"
          label="Bill No.*"
          :error="!!errors.voucher_no"
          :error-message="errors.voucher_no"
        />
        <div
          v-if="formDefaults.options?.enable_discount_in_voucher && !isTemplate"
          class="col-md-6 col-12 row q-col-gutter-md"
        >
          <div :class="['Percent', 'Amount'].includes(fields.discount_type) ? 'col-6' : 'col-12'">
            <n-auto-complete
              v-model="fields.discount_type"
              label="Discount"
              :error="errors.discount_type"
              :modal-component="checkPermissions('purchasediscount.create') ? PurchaseDiscountForm : null"
              :options="discountOptionsComputed"
            />
          </div>
          <div class="col-6 row">
            <div v-if="fields.discount_type === 'Amount' || fields.discount_type === 'Percent'" :class="formDefaults.options?.show_trade_discount_in_voucher ? 'col-6' : 'col-12'">
              <q-input
                v-model.number="fields.discount"
                class="col-6"
                label="Discount"
                :error="!!errors.discount"
                :error-message="errors.discount"
              />
            </div>
            <div v-if="formDefaults.options?.show_trade_discount_in_voucher && ['Percent', 'Amount'].includes(fields.discount_type)" class="col-3 row">
              <q-checkbox v-model="fields.trade_discount" label="Trade Discount?" />
            </div>
          </div>
        </div>
        <div v-if="!isTemplate" class="col-md-6 col-12">
          <date-picker
            v-model="fields.date"
            label="Date *"
            :error="!!errors.date"
            :error-message="errors.date"
          />
        </div>

        <div class="col-md-6 col-12">
          <n-auto-complete-v2
            v-model="fields.payment_mode"
            emit-value
            map-options
            label="Payment Mode"
            option-label="name"
            option-value="id"
            :endpoint="`/api/company/${$route.params.company}/purchase-vouchers/create-defaults/payment_modes`"
            :error="errors.payment_mode"
            :error-message="errors.payment_mode"
            :options="modeOptionsComputed"
            :static-option="isEdit ? fields.selected_payment_mode_obj : formDefaults.options?.default_payment_mode_obj"
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
        <date-picker
          v-if="formDefaults.options?.enable_due_date_in_voucher && !isTemplate"
          v-model="fields.due_date"
          class="col-md-6 col-12"
          label="Due Date"
          :error="!!errors?.due_date"
          :error-message="errors?.due_date"
          :to-limit="fields.date"
        />
      </div>
    </q-card-section>
  </q-card>
  <InvoiceTable
    v-if="formDefaults.collections"
    v-model="fields.rows"
    used-in="purchase"
    :discount-options="discountOptionsComputed"
    :enable-row-description="formDefaults.options?.enable_row_description"
    :errors="!!errors.rows ? errors.rows : null"
    :item-options="formDefaults.collections ? formDefaults.collections.items : null"
    :main-discount="{
      discount_type: fields.discount_type,
      discount: fields.discount,
    }"
    :missing-fields-config="{
      enabled: true,
      fields: {
        code: formDefaults?.options?.require_item_code,
        hs_code: formDefaults?.options?.require_item_hs_code,
      },
    }"
    :show-row-trade-discount="formDefaults.options?.show_trade_discount_in_row"
    :tax-options="formDefaults.collections?.tax_schemes"
    :unit-options="formDefaults.collections ? formDefaults.collections.units : null"
    @delete-row-err="(index, deleteObj) => deleteRowErr(index, errors, deleteObj)"
  />
  <q-card v-if="formDefaults.options?.enable_landed_costs" class="q-mx-lg q-mt-md">
    <q-card-section :style="{ paddingLeft: '0px', paddingRight: '0px' }">
      <div class="row items-center q-mb-md">
        <q-checkbox v-model="showLandedCosts" label="Landed Costs" />
      </div>
      <div v-if="showLandedCosts">
        <div class="row q-col-gutter-md q-mb-md">
          <div class="col-12">
            <q-btn
              color="primary"
              icon="add"
              label="Add Cost"
              @click="addLandedCostRow"
            />
          </div>
        </div>
        <q-table
          v-if="fields.landed_cost_rows?.length"
          bordered
          flat
          hide-pagination
          row-key="type"
          :columns="landedCostColumns"
          :rows="fields.landed_cost_rows"
        >
          <template #body-cell-actions="cellProps">
            <q-td :props="cellProps">
              <q-btn
                flat
                round
                color="negative"
                icon="delete"
                @click="removeLandedCostRow(cellProps.rowIndex)"
              />
            </q-td>
          </template>
          <template #body-cell-type="cellProps">
            <q-td :props="cellProps">
              <q-select
                v-model="cellProps.row.type"
                dense
                emit-value
                map-options
                options-dense
                :options="landedCostTypes"
                @update:model-value="handleTypeChange(cellProps.row)"
              />
            </q-td>
          </template>
          <template #body-cell-is_percentage="cellProps">
            <q-td :props="cellProps">
              <q-toggle
                v-model="cellProps.row.is_percentage"
                class="full-width"
                :label="cellProps.row.is_percentage ? 'Percentage' : 'Fixed'"
              />
            </q-td>
          </template>
          <template #body-cell-amount="cellProps">
            <q-td :props="cellProps">
              <div class="row items-center no-wrap">
                <q-input
                  v-model="cellProps.row.value"
                  dense
                  class="col"
                  type="number"
                  :error="!!errors?.landed_cost_rows?.[cellProps.rowIndex]?.value"
                  :error-message="errors?.landed_cost_rows?.[cellProps.rowIndex]?.value"
                  :value="cellProps.row.amount"
                />
                <span class="q-ml-sm text-no-wrap">{{ cellProps.row.is_percentage ? '%' : cellProps.row.currency }}</span>
                <div v-if="cellProps.row.amount" class="q-ml-sm text-grey-6 text-no-wrap">
                  (<FormattedNumber
                    type="currency"
                    :currency="loginStore.companyInfo.currency_code"
                    :value="cellProps.row.amount"
                  />)
                </div>
              </div>
            </q-td>
          </template>
          <template #body-cell-currency="cellProps">
            <q-td :props="cellProps">
              <q-select
                v-model="cellProps.row.currency"
                dense
                emit-value
                map-options
                options-dense
                :disable="cellProps.row.is_percentage"
                :options="AVAILABLE_CURRENCIES"
              />
            </q-td>
          </template>
          <template #body-cell-tax_scheme="cellProps">
            <q-td :props="cellProps">
              <n-auto-complete-v2
                v-model="cellProps.row.tax_scheme_id"
                dense
                emit-value
                map-options
                option-label="name"
                option-value="id"
                :endpoint="`/api/company/${$route.params.company}/purchase-vouchers/create-defaults/tax_schemes`"
                :options="formDefaults.collections?.tax_schemes"
              >
                <template #append>
                  <q-icon
                    v-if="cellProps.row.tax_scheme_id"
                    class="cursor-pointer"
                    name="close"
                    @click.stop.prevent="cellProps.row.tax_scheme_id = null"
                  />
                </template>
              </n-auto-complete-v2>
            </q-td>
          </template>
          <template #body-cell-credit_account="cellProps">
            <q-td :props="cellProps">
              <n-auto-complete-v2
                v-model="cellProps.row.credit_account_id"
                dense
                emit-value
                map-options
                option-label="name"
                option-value="id"
                :endpoint="`/api/company/${$route.params.company}/purchase-vouchers/create-defaults/landed_cost_credit_accounts`"
                :options="formDefaults.collections?.landed_cost_credit_accounts"
              >
                <template #append>
                  <q-icon
                    v-if="cellProps.row.credit_account_id"
                    class="cursor-pointer"
                    name="close"
                    @click.stop.prevent="cellProps.row.credit_account_id = null"
                  />
                </template>
              </n-auto-complete-v2>
            </q-td>
          </template>
          <template #body-cell-description="cellProps">
            <q-td :props="cellProps">
              <q-input
                v-model="cellProps.row.description"
                dense
                :error="!!errors?.landed_cost_rows?.[cellProps.rowIndex]?.description"
                :error-message="errors?.landed_cost_rows?.[cellProps.rowIndex]?.description"
              />
            </q-td>
          </template>
          <template #bottom-row>
            <q-tr>
              <q-td class="text-right" colspan="6">
                Average rate per item:
              </q-td>
              <q-td class="text-left text-bold" colspan="2">
                <FormattedNumber
                  type="currency"
                  :currency="loginStore.companyInfo.currency_code"
                  :value="averageRate"
                />
              </q-td>
            </q-tr>
          </template>
        </q-table>
      </div>
    </q-card-section>
  </q-card>
  <div class="row q-px-lg">
    <div class="col-12 col-md-6 row">
      <!-- <q-input
            v-model="fields.remarks"
            label="Remarks"
            type="textarea"
          ></q-input> -->
      <q-input
        v-model="fields.remarks"
        autogrow
        class="col-12 col-md-10"
        label="Remarks"
        type="textarea"
        :error="!!errors?.remarks"
        :error-message="errors?.remarks"
      />
    </div>
    <div class="col-12 col-md-6 row justify-between">
      <div>
        <q-checkbox v-model="fields.is_import" class="q-mt-md col-3" label="Import?" />
      </div>
      <!-- TODO: add sales agent form -->
    </div>
  </div>
</template>
