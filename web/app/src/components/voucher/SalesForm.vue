<template>
  <q-card class="q-mx-lg q-pt-md">
    <q-card-section>
      <div class="row q-col-gutter-md">
        <div class="col-md-6 col-12" v-if="formDefaults.options?.enable_import_challan">
          <q-btn color="blue" @click="importChallanModal = true" data-testid="import-challan-btn"
            label="Import challan(s)"></q-btn>
          <div v-if="fields.challans && fields.challans.length > 0">
            <q-input dense v-model="fields.challan_numbers" disable label="Import challan(s)"></q-input>
          </div>
          <q-dialog v-model="importChallanModal" @before-hide="
            errors && delete errors?.fiscal_year && delete errors?.invoice_no
            ">
            <q-card style="min-width: min(60vw, 400px)">
              <q-card-section class="bg-grey-4">
                <div class="text-h6">
                  <span>Add Reference Challan(s)</span>
                </div>
              </q-card-section>

              <q-card-section class="q-mx-lg">
                <q-input v-model.number="referenceFormData.invoice_no" label="Challan No.*" autofocus type="number"
                  :error="errors?.invoice_no ?? null" :error-message="errors?.invoice_no"
                  data-testid="challan-no-input"></q-input>
                <q-select class="q-mt-md" label="Fiscal Year" v-model="referenceFormData.fiscal_year"
                  :options="formDefaults.options?.fiscal_years" option-value="id" option-label="name" map-options
                  emit-value data-testid="fiscal-year-select" :error="errors?.fiscal_year ?? null"
                  :error-message="errors?.fiscal_year"></q-select>
                <div class="row justify-end q-mt-lg">
                  <q-btn color="green" label="Add" size="md" @click="fetchInvoice(fields)"
                    data-testid="add-reference-btn"></q-btn>
                </div>
              </q-card-section>
            </q-card>
          </q-dialog>
        </div>
        <div class="col-md-6 col-12">
          <div class="row">
            <div class="col-10">
              <q-input v-model="fields.customer_name" label="Customer Name" :error-message="errors?.customer_name"
                :error="errors?.customer_name ?? null" v-if="customerMode" data-testid="customer-name-input">
              </q-input>
              <n-auto-complete-v2 v-else v-model="fields.party" :options="formDefaults.collections?.parties"
                label="Party" :error="errors?.party ? errors?.party : null" :modal-component="checkPermissions('PartyCreate') ? PartyForm : null
                  " :staticOption="fields.selected_party_obj" endpoint="/v1/sales-voucher/create-defaults/parties"
                :emitObj="true" @updateObj="onPartyChange" />
            </div>

            <div class="col-2 row justify-center q-py-md">
              <q-btn flat size="md" @click="() => switchMode(fields)" data-testid="switch-account-group-btn">
                <q-icon name="mdi-account-group"></q-icon>
              </q-btn>
            </div>
          </div>
          <div>
            <n-auto-complete v-if="!customerMode && fields.party && aliases.length > 0" v-model="fields.customer_name"
              class="col-md-6 col-12" label="Name on Invoice" :options="aliases" :modal-component="checkPermissions('PartyAliasCreate') ? PartyAlias : null
                " :error="errors?.customer_name ? errors?.customer_name : null" data-testid="alias-select">
            </n-auto-complete>
          </div>
        </div>

        <date-picker v-if="formDefaults.options?.enable_sales_date_edit" label="Invoice Date*" v-model="fields.date"
          class="col-md-6 col-12" :error="errors?.date ? errors?.date : null"
          :error-message="errors?.date"></date-picker>
        <DateInputDisabled v-else :date="fields.date" class="col-md-6 col-12" label="Invoice Date*" />
        <q-input v-model="fields.address" class="col-md-6 col-12" label="Address" :error-message="errors?.address"
          :error="!!errors?.address" data-testid="address-input"></q-input>
        <date-picker v-if="formDefaults.options?.enable_due_date_in_voucher" label="Due Date" v-model="fields.due_date"
          class="col-md-6 col-12" :error="errors?.due_date ? errors.due_date : null" :error-message="errors?.due_date"
          :toLimit="fields.date" data-testid="due-date"></date-picker>
        <div class="col-md-6 col-12 row q-col-gutter-md">
          <div :class="['Percent', 'Amount'].includes(fields.discount_type)
              ? 'col-6'
              : 'col-12'
            " data-testid="overall-discount-type-div">
            <n-auto-complete v-model="fields.discount_type" label="Discount"
              :error="errors?.discount_type ? errors?.discount_type : null" :options="staticOptions.discount_types.concat(
                formDefaults.collections?.discounts
              )
                " :modal-component="checkPermissions('SalesDiscountCreate')
                  ? SalesDiscountForm
                  : null
                ">
            </n-auto-complete>
          </div>
          <div class="col-6 row">
            <div :class="formDefaults.options?.show_trade_discount_in_voucher
                ? 'col-6'
                : 'col-12'
              " v-if="
                fields.discount_type === 'Amount' ||
                fields.discount_type === 'Percent'
              ">
              <q-input class="col-6" v-model.number="fields.discount" label="Discount" :error-message="errors?.discount"
                :error="!!errors?.discount" data-testid="discount-input"></q-input>
            </div>
            <div class="col-3 row" v-if="
              formDefaults.options?.show_trade_discount_in_voucher &&
              ['Percent', 'Amount'].includes(fields.discount_type)
            ">
              <q-checkbox v-model="fields.trade_discount" label="Trade Discount?"
                data-testid="trade-discount-input"></q-checkbox>
            </div>
          </div>
        </div>
      </div>
      <div class="row q-col-gutter-md">
        <div class="col-12 col-md-6">
          <n-auto-complete-v2 v-model="fields.payment_mode" label="Payment Mode *"
            endpoint="/v1/sales-voucher/create-defaults/payment_modes"
            :error="errors?.payment_mode ? errors?.payment_mode : null" :options="modeOptionsComputed" :staticOption="isEdit
                ? fields.selected_payment_mode_obj
                : formDefaults.options?.default_payment_mode_obj
              " @updateObj="onPaymentModeChange" data-testid="payment-mode-select" :emitObj="true" :mapOptions="true">
            <template v-slot:append>
              <q-icon v-if="fields.payment_mode !== null" class="cursor-pointer" name="clear"
                @click.stop.prevent="fields.payment_mode = null" /></template>
          </n-auto-complete-v2>
        </div>
      </div>
    </q-card-section>
  </q-card>
  <invoice-table v-if="formDefaults.collections" :itemOptions="formDefaults.collections ? formDefaults.collections.items : null
    " :unitOptions="formDefaults.collections ? formDefaults.collections.units : null
      " :discountOptions="staticOptions.discount_types.concat(formDefaults.collections?.discounts)
      " :taxOptions="formDefaults.collections?.tax_schemes" v-model="fields.rows" :mainDiscount="{
      discount_type: fields.discount_type,
      discount: fields.discount,
    }" :errors="errors?.rows ? errors.rows : null" @deleteRowErr="deleteRowErr"
    :enableRowDescription="formDefaults.options?.enable_row_description"
    :showRowTradeDiscount="formDefaults.options?.show_trade_discount_in_row"
    :inputAmount="formDefaults.options?.enable_amount_entry"
    :showRateQuantity="formDefaults.options?.show_rate_quantity_in_voucher" :isFifo="formDefaults.options?.enable_fifo"
    usedIn="sales" :hasChallan="!!(fields.challans && fields.challans.length > 0)"></invoice-table>
  <div class="row q-px-lg">
    <div class="col-12 col-md-6 row">
      <q-input v-model="fields.remarks" label="Remarks" type="textarea" autogrow class="col-12 col-md-10"
        :error="!!errors?.remarks" :error-message="errors?.remarks" data-testid="remarks-input" />
    </div>
    <div class="col-12 col-md-6 row justify-between">
      <div class="col-3">
        <q-checkbox label="Export?" v-model="fields.is_export" class="q-mt-md col-3"
          data-testid="export-checkbox"></q-checkbox>
      </div>
      <div class="col-9">
        <n-auto-complete-v2 v-if="loginStore.companyInfo.enable_sales_agents" v-model="fields.sales_agent"
          label="Sales Agent" class="col-8" :error="errors?.sales_agent"
          :options="formDefaults.collections?.sales_agents" :endpoint="`v1/sales-voucher/create-defaults/sales_agents`"
          :staticOption="fields.selected_sales_agent_obj" data-testid="sales-agent-select"></n-auto-complete-v2>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useLoginStore } from 'src/stores/login-info'
import checkPermissions from 'src/composables/checkPermissions'
import PartyForm from 'src/pages/party/PartyForm.vue'
import PartyAlias from 'src/pages/party/PartyAlias.vue'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import SalesDiscountForm from 'src/pages/sales/discount/SalesDiscountForm.vue'

const importChallanModal = ref(false)

const loginStore = useLoginStore()

const { $q } = useQuasar()

const props = defineProps({
  formDefaults: {
    type: Object,
    required: true,
  },
  errors: {
    type: Object,
    required: true,
  },
  isEdit: {
    type: Boolean,
    required: false,
  },
})

const fields = defineModel('fields')

const customerMode = defineModel('customerMode')

const aliases = defineModel('aliases')

const referenceFormData = ref({
  invoice_no: null,
  fiscal_year: loginStore.companyInfo.current_fiscal_year_id || null,
})

const fetchInvoice = async (fields) => {
  if (!errors.value) errors.value = {}
  delete errors.value.fiscal_year
  delete errors.value.invoice_no

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
      errors.value.invoice_no = 'The invoice has already been added!'
    } else {
      const url = 'v1/challan/by-voucher-no/'
      try {
        const data = await useApi(
          url +
          `?invoice_no=${referenceFormData.value.invoice_no}&fiscal_year=${referenceFormData.value.fiscal_year}`
        )
        errors.value = {}
        const response = { ...data }

        if (
          (fields.party && fields.party !== response.party) ||
          (fields.customer_name &&
            fields.customer_name !== response.customer_name)
        ) {
          $q.notify({
            color: 'red-6',
            message:
              'A single challan can be issued to a single party/customer only',
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
          message =
            err.data?.detail ||
            'Server Error! Please contact us with the problem.'
        }
        $q.notify({
          color: 'red-6',
          message: message,
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
      aliases.value = [
        { name: obj.name, id: null },
        ...obj.aliases.map((item) => ({ name: item, id: item })),
      ]
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
  discount_types: discount_types,
  modes: modes,
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
  if (props.formDefaults.value?.collections?.payment_modes?.results) {
    obj.results = obj.results.concat(
      props.formDefaults.value.collections.payment_modes.results
    )
    Object.assign(
      obj.pagination,
      props.formDefaults.value.collections.payment_modes.pagination
    )
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
</script>
