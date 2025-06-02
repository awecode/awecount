<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import PartyForm from 'src/pages/party/PartyForm.vue'
import PurchaseDiscountForm from 'src/pages/purchase/discounts/PurchaseDiscountForm.vue'
import { useLoginStore } from 'src/stores/login-info'
import { useRoute } from 'vue-router'
import InvoiceTable from './InvoiceTable.vue'
import LandedCosts from './LandedCosts.vue'

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
  <LandedCosts
    :errors="errors"
    :fields="fields"
    :form-defaults="formDefaults"
  />
  <div class="row q-px-lg">
    <div class="col-12 col-md-6 row">
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
    </div>
  </div>
</template>
