<script>
import { discount_types, modes } from 'src/helpers/constants/invoice'
import CategoryForm from 'src/pages/account/category/CategoryForm.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import PurchaseDiscountForm from 'src/pages/purchase/discounts/PurchaseDiscountForm.vue'
import { useLoginStore } from 'src/stores/login-info'

export default {
  setup() {
    const route = useRoute()
    const store = useLoginStore()
    const endpoint = `/api/company/${route.params.company}/purchase-vouchers/`
    const openDatePicker = ref(false)
    const $q = useQuasar()
    const staticOptions = {
      discount_types,
      modes,
    }
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/purchase-voucher/list/',
    })
    const importPurchaseOrder = ref(false)
    const referenceFormData = ref({
      invoice_no: null,
      fiscal_year: store.companyInfo.current_fiscal_year_id || null,
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Update Purchases/Expenses' : 'Add Purchases/Expenses'} | Awecount`,
      }
    })
    const deleteRowErr = (index, errors, deleteObj) => {
      if (deleteObj) {
        if (!formData.fields.value.deleted_rows) {
          formData.fields.value.deleted_rows = []
        }
        formData.fields.value.deleted_rows.push(deleteObj)
      }
      if (errors.rows) errors.rows.splice(index, 1)
    }
    const onSubmitClick = async (status) => {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      const data = await formData.submitForm()
      if (data && data.hasOwnProperty('error')) {
        formData.fields.value.status = originalStatus
      }
    }
    formData.fields.value.date = formData.today
    formData.fields.value.due_date = formData.today
    formData.fields.value.is_import = false
    watch(
      () => formData.formDefaults.value,
      () => {
        if (!formData.isEdit.value) {
          if (formData.formDefaults.value.fields?.mode) {
            if (isNaN(formData.formDefaults.value.fields?.mode)) {
              formData.fields.value.mode = formData.formDefaults.value.fields.mode
            } else {
              formData.fields.value.mode = Number(formData.formDefaults.value.fields.mode)
            }
          } else {
            formData.fields.value.mode = 'Credit'
          }
        }
      },
    )
    const fetchInvoice = async (data) => {
      if (!formData?.errors?.value) formData.errors.value = {}
      delete formData.errors.value.fiscal_year
      delete formData.errors.value.invoice_no
      const fetchData = data || { invoice_no: referenceFormData.value.invoice_no, fiscal_year: referenceFormData.value.fiscal_year }
      if (fetchData.invoice_no && fetchData.fiscal_year) {
        if (formData.fields.value.purchase_orders && formData.fields.value.purchase_orders.includes(fetchData.invoice_no)) {
          $q.notify({
            color: 'red-6',
            message: 'Invoice Already Exists!',
            icon: 'report_problem',
            position: 'top-right',
          })
          formData.errors.value.invoice_no = 'The invoice has already been added!'
        } else {
          const url = 'v1/purchase-order/by-voucher-no/'
          useApi(`${url}?invoice_no=${fetchData.invoice_no}&fiscal_year=${fetchData.fiscal_year}`)
            .then((data) => {
              const response = { ...data }
              if (formData.fields.value.purchase_orders) {
                if (formData.fields.value.party && formData.fields.value.party !== response.party) {
                  $q.notify({
                    color: 'red-6',
                    message: 'A single purchase order can be issued to a single party only',
                    icon: 'report_problem',
                    position: 'top-right',
                  })
                  return
                }
                formData.fields.value.purchase_orders.push(data.id)
              } else {
                formData.fields.value.purchase_orders = [data.id]
              }
              if (formData.fields.value.purchase_order_numbers) {
                formData.fields.value.purchase_order_numbers.push(response.voucher_no)
              } else {
                formData.fields.value.purchase_order_numbers = [response.voucher_no]
              }
              const removeArr = ['id', 'date', 'voucher_meta', 'print_count', 'issue_datetime', 'is_export', 'status', 'due_date', 'rows', 'date', 'remarks', 'voucher_no']
              removeArr.forEach((item) => {
                delete data[item]
              })
              for (const key in data) {
                formData.fields.value[key] = data[key]
                // if (key === )
              }
              if (response.rows && response.rows.length > 0) {
                if (!formData.fields.value.rows) formData.fields.value.rows = []
                response.rows.forEach((row) => {
                  delete row.id
                  formData.fields.value.rows.push(row)
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
        if (!formData?.errors?.value) formData.errors.value = {}
        if (!referenceFormData.value.invoice_no) {
          formData.errors.value.invoice_no = 'Invoice Number is required!'
        }
        if (!referenceFormData.value.fiscal_year) {
          formData.errors.value.fiscal_year = 'Fiscal Year is required!'
        }
      }
    }
    onMounted(() => {
      const route = useRoute()
      if (route.query.purchase_order && route.query.fiscal_year) {
        const data = { invoice_no: route.query.purchase_order, fiscal_year: route.query.fiscal_year }
        fetchInvoice(data)
      }
    })
    watch(
      () => formData.formDefaults.value,
      () => {
        if (formData.formDefaults.value.fields?.hasOwnProperty('trade_discount')) {
          formData.fields.value.trade_discount = formData.formDefaults.value.fields?.trade_discount
        }
      },
    )
    const discountOptionsComputed = computed(() => {
      if (formData?.formDefaults.value?.collections?.discounts) {
        return staticOptions.discount_types.concat(formData.formDefaults.value.collections.discounts)
      } else {
        return staticOptions.discount_types
      }
    })
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
    return {
      ...formData,
      CategoryForm,
      PartyForm,
      PurchaseDiscountForm,
      openDatePicker,
      staticOptions,
      deleteRowErr,
      onSubmitClick,
      checkPermissions,
      importPurchaseOrder,
      referenceFormData,
      fetchInvoice,
      discountOptionsComputed,
      modeOptionsComputed,
    }
  },
}
</script>

<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Purchase / Expense</span>
          <span v-else>Update Purchase / Expense</span>
        </div>
      </q-card-section>
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div v-if="formDefaults.options?.enable_purchase_order_import" class="col-md-6 col-12">
              <q-btn color="blue" label="Import purchase order(s)" @click="importPurchaseOrder = true" />
              <div v-if="fields.purchase_orders && fields.purchase_orders.length > 0">
                <q-input v-model="fields.purchase_order_numbers" dense disable label="Purchase Order(s)" />
              </div>
              <q-dialog v-model="importPurchaseOrder">
                <q-card style="min-width: min(60vw, 400px)">
                  <q-card-section class="bg-grey-4 flex justify-between">
                    <div class="text-h6">
                      <span>Add Reference Purchase Order(s)</span>
                    </div>
                    <q-btn v-close-popup icon="close" class="text-white bg-red-500 opacity-95" flat round dense />
                  </q-card-section>

                  <q-card-section class="q-mx-lg">
                    <q-input v-model.number="referenceFormData.invoice_no" label="Purchase Order No.*" autofocus type="number" :error="!!errors?.invoice_no" :error-message="errors?.invoice_no" />
                    <q-select v-model="referenceFormData.fiscal_year" class="q-mt-md" label="Fiscal Year" :options="formDefaults.options?.fiscal_years" option-value="id" option-label="name" map-options emit-value :error="!!errors?.fiscal_year" :error-message="errors?.fiscal_year" />
                    <div class="row justify-end q-mt-lg">
                      <q-btn color="green" label="Add" size="md" @click="fetchInvoice()" />
                    </div>
                  </q-card-section>
                </q-card>
              </q-dialog>
            </div>
            <div class="col-md-6 col-12">
              <n-auto-complete-v2 v-model="fields.party" :options="formDefaults.collections?.parties" label="Party" :error="errors?.party ? errors?.party : ''" :static-option="fields.selected_party_obj" :endpoint="`/api/company/${$route.params.company}/sales-voucher/create-defaults/parties`" :modal-component="checkPermissions('party.create') ? PartyForm : null" />
            </div>
            <q-input v-model="fields.voucher_no" class="col-md-6 col-12" label="Bill No.*" :error-message="errors.voucher_no" :error="!!errors.voucher_no" />
            <div class="col-md-6 col-12 row q-col-gutter-md">
              <div :class="['Percent', 'Amount'].includes(fields.discount_type) ? 'col-6' : 'col-12'">
                <n-auto-complete v-model="fields.discount_type" label="Discount" :error="errors.discount_type" :options="discountOptionsComputed" :modal-component="checkPermissions('purchasediscount.create') ? PurchaseDiscountForm : null" />
              </div>
              <div class="col-6 row">
                <div v-if="fields.discount_type === 'Amount' || fields.discount_type === 'Percent'" :class="formDefaults.options?.show_trade_discount_in_voucher ? 'col-6' : 'col-12'">
                  <q-input v-model.number="fields.discount" class="col-6" label="Discount" :error-message="errors.discount" :error="!!errors.discount" />
                </div>
                <div v-if="formDefaults.options?.show_trade_discount_in_voucher && ['Percent', 'Amount'].includes(fields.discount_type)" class="col-3 row">
                  <q-checkbox v-model="fields.trade_discount" label="Trade Discount?" />
                </div>
              </div>
            </div>
            <div class="col-md-6 col-12">
              <date-picker v-model="fields.date" label="Date *" :error-message="errors.date" :error="!!errors.date" />
            </div>
          </div>

          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <n-auto-complete-v2 v-model="fields.payment_mode" label="Payment Mode" :error-message="errors.payment_mode" :error="!!errors.payment_mode" :static-option="isEdit ? fields.selected_payment_mode_obj : formDefaults.options?.default_payment_mode_obj" :options="modeOptionsComputed" :endpoint="`/api/company/${$route.params.company}/purchase-vouchers/create-defaults/payment_modes`" option-value="id" option-label="name" map-options emit-value>
                <template #append>
                  <q-icon v-if="fields.payment_mode !== null" class="cursor-pointer" name="clear" @click.stop.prevent="fields.payment_mode = null" />
                </template>
              </n-auto-complete-v2>
            </div>
            <date-picker v-if="formDefaults.options?.enable_due_date_in_voucher" v-model="fields.due_date" label="Due Date" class="col-md-6 col-12" :error-message="errors?.due_date" :error="!!errors?.due_date" :to-limit="fields.date" />
          </div>
          <!-- {{ fields.date }} -->
        </q-card-section>
      </q-card>
      <invoice-table
        v-if="formDefaults.collections"
        v-model="fields.rows"
        :item-options="formDefaults.collections ? formDefaults.collections.items : null"
        used-in="purchase"
        :unit-options="formDefaults.collections ? formDefaults.collections.units : null"
        :discount-options="discountOptionsComputed"
        :tax-options="formDefaults.collections?.tax_schemes"
        :main-discount="{
          discount_type: fields.discount_type,
          discount: fields.discount,
        }"
        :errors="!!errors.rows ? errors.rows : null"
        :enable-row-description="formDefaults.options?.enable_row_description"
        :show-row-trade-discount="formDefaults.options?.show_trade_discount_in_row"
        @delete-row-err="(index, deleteObj) => deleteRowErr(index, errors, deleteObj)"
      />
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
            <q-checkbox v-model="fields.is_import" label="Import?" class="q-mt-md col-3" />
          </div>
          <!-- TODO: add sales agent form -->
        </div>
      </div>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn v-if="checkPermissions('purchasevoucher.create') && !isEdit" :loading="loading" color="orange" label="Save Draft" type="submit" @click.prevent="() => onSubmitClick('Draft')" />
        <q-btn v-if="checkPermissions('purchasevoucher.create') && isEdit && fields.status === 'Draft'" :loading="loading" color="orange" label="Update Draft" type="submit" @click.prevent="() => onSubmitClick('Draft')" />
        <q-btn v-if="checkPermissions('purchasevoucher.create') && !isEdit" :loading="loading" color="green" label="Issue" @click.prevent="() => onSubmitClick('Issued')" />
        <q-btn v-if="checkPermissions('purchasevoucher.create') && isEdit" :loading="loading" color="green" :label="fields.status === 'Draft' ? 'Issue from Draft' : 'Update'" @click.prevent="() => onSubmitClick(fields.status === 'Draft' ? 'Issued' : fields.status)" />
      </div>
    </q-card>
  </q-form>
</template>
