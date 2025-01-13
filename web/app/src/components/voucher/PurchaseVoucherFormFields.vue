<template>
  <q-card class="q-mx-lg q-pt-md">
    <q-card-section>
      <div class="row q-col-gutter-md">
        <div class="col-md-6 col-12" v-if="formDefaults.options?.enable_purchase_order_import">
          <q-btn color="blue" @click="importPurchaseOrder = true" label="Import purchase order(s)"></q-btn>
          <div v-if="fields.purchase_orders && fields.purchase_orders.length > 0">
            <q-input dense v-model="fields.purchase_order_numbers" disable label="Purchase Order(s)"></q-input>
          </div>
          <q-dialog v-model="importPurchaseOrder">
            <q-card style="min-width: min(60vw, 400px)">
              <q-card-section class="bg-grey-4 flex justify-between">
                <div class="text-h6">
                  <span>Add Reference Purchase Order(s)</span>
                </div>
                <q-btn icon="close" class="text-white bg-red-500 opacity-95" flat round dense v-close-popup />
              </q-card-section>

              <q-card-section class="q-mx-lg">
                <q-input v-model.number="referenceFormData.invoice_no" label="Purchase Order No.*" autofocus type="number" :error="!!errors?.invoice_no" :error-message="errors?.invoice_no"></q-input>
                <q-select class="q-mt-md" label="Fiscal Year" v-model="referenceFormData.fiscal_year" :options="formDefaults.options?.fiscal_years" option-value="id" option-label="name" map-options emit-value :error="!!errors?.fiscal_year" :error-message="errors?.fiscal_year"></q-select>
                <div class="row justify-end q-mt-lg">
                  <q-btn color="green" label="Add" size="md" @click="fetchInvoice()"></q-btn>
                </div>
              </q-card-section>
            </q-card>
          </q-dialog>
        </div>
        <div class="col-md-6 col-12">
          <n-auto-complete-v2 v-model="fields.party" :options="formDefaults.collections?.parties" label="Party" :error="errors?.party ? errors?.party : ''" :staticOption="fields.selected_party_obj" endpoint="/v1/sales-voucher/create-defaults/parties" :modal-component="checkPermissions('PartyCreate') ? PartyForm : null" />
        </div>
        <q-input v-if="!isTemplate" class="col-md-6 col-12" label="Bill No.*" v-model="fields.voucher_no" :error-message="errors.voucher_no" :error="!!errors.voucher_no"></q-input>
        <div class="col-md-6 col-12 row q-col-gutter-md">
          <div :class="['Percent', 'Amount'].includes(fields.discount_type) ? 'col-6' : 'col-12'">
            <n-auto-complete v-model="fields.discount_type" label="Discount" :error="errors.discount_type" :options="discountOptionsComputed" :modal-component="checkPermissions('PurchaseDiscountCreate') ? PurchaseDiscountForm : null"></n-auto-complete>
          </div>
          <div class="col-6 row">
            <div :class="formDefaults.options?.show_trade_discount_in_voucher ? 'col-6' : 'col-12'" v-if="fields.discount_type === 'Amount' || fields.discount_type === 'Percent'">
              <q-input class="col-6" v-model.number="fields.discount" label="Discount" :error-message="errors.discount" :error="!!errors.discount"></q-input>
            </div>
            <div class="col-3 row" v-if="formDefaults.options?.show_trade_discount_in_voucher && ['Percent', 'Amount'].includes(fields.discount_type)">
              <q-checkbox v-model="fields.trade_discount" label="Trade Discount?"></q-checkbox>
            </div>
          </div>
        </div>
        <div class="col-md-6 col-12" v-if="!isTemplate">
          <date-picker v-model="fields.date" label="Date *" :error-message="errors.date" :error="!!errors.date"></date-picker>
        </div>
      </div>

      <div class="row q-col-gutter-md">
        <div class="col-md-6 col-12">
          <n-auto-complete-v2 v-model="fields.payment_mode" label="Payment Mode" :error-message="errors.payment_mode" :error="errors.payment_mode" :staticOption="isEdit ? fields.selected_payment_mode_obj : formDefaults.options?.default_payment_mode_obj" :options="modeOptionsComputed" endpoint="v1/purchase-vouchers/create-defaults/payment_modes" option-value="id" option-label="name" map-options emit-value>
            <template v-slot:append>
              <q-icon v-if="fields.payment_mode !== null" class="cursor-pointer" name="clear" @click.stop.prevent="fields.payment_mode = null" />
            </template>
          </n-auto-complete-v2>
        </div>
        <date-picker v-if="formDefaults.options?.enable_due_date_in_voucher && !isTemplate" label="Due Date" v-model="fields.due_date" class="col-md-6 col-12" :error-message="errors?.due_date" :error="!!errors?.due_date" :toLimit="fields.date"></date-picker>
      </div>
      <!-- {{ fields.date }} -->
    </q-card-section>
  </q-card>
  <invoice-table
    v-if="formDefaults.collections"
    :itemOptions="formDefaults.collections ? formDefaults.collections.items : null"
    usedIn="purchase"
    :unitOptions="formDefaults.collections ? formDefaults.collections.units : null"
    :discountOptions="discountOptionsComputed"
    :taxOptions="formDefaults.collections?.tax_schemes"
    v-model="fields.rows"
    :mainDiscount="{
      discount_type: fields.discount_type,
      discount: fields.discount,
    }"
    :errors="!!errors.rows ? errors.rows : null"
    @deleteRowErr="(index, deleteObj) => deleteRowErr(index, errors, deleteObj)"
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
      <q-input v-model="fields.remarks" label="Remarks" type="textarea" autogrow class="col-12 col-md-10" :error="!!errors?.remarks" :error-message="errors?.remarks" />
    </div>
    <div class="col-12 col-md-6 row justify-between">
      <div>
        <q-checkbox label="Import?" v-model="fields.is_import" class="q-mt-md col-3"></q-checkbox>
      </div>
      <!-- TODO: add sales agent form -->
    </div>
  </div>
</template>

<script setup>
import PartyForm from 'src/pages/party/PartyForm.vue'
import PurchaseDiscountForm from 'src/pages/purchase/discounts/PurchaseDiscountForm.vue'
import checkPermissions from 'src/composables/checkPermissions'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import { useLoginStore } from 'src/stores/login-info'

const loginStore = useLoginStore()

const staticOptions = {
  discount_types: discount_types,
  modes: modes,
}
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
const fields = defineModel('fields')

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
      const url = 'v1/purchase-order/by-voucher-no/'
      useApi(url + `?invoice_no=${fetchData.invoice_no}&fiscal_year=${fetchData.fiscal_year}`)
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
          } else fields.value.purchase_orders = [data.id]
          if (fields.value.purchase_order_numbers) {
            fields.value.purchase_order_numbers.push(response.voucher_no)
          } else fields.value.purchase_order_numbers = [response.voucher_no]
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
  } else return staticOptions.discount_types
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
  if (!!errors.rows) errors.rows.splice(index, 1)
}

watch(
  () => props.formDefaults,
  () => {
    if (!props.isEdit) {
      if (props.formDefaults.fields?.mode) {
        if (isNaN(props.formDefaults.fields?.mode)) {
          fields.value.mode = props.formDefaults.fields.mode
        } else {
          fields.value.mode = Number(props.formDefaults.fields.mode)
        }
      } else fields.value.mode = 'Credit'
    }

    if (props.formDefaults.fields?.hasOwnProperty('trade_discount')) {
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
