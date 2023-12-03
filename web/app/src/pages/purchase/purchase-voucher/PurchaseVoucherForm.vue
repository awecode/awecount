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
            <div class="col-md-6 col-12" v-if="formDefaults.options?.enable_purchase_order_import">
              <q-btn color="blue" @click="importPurchaseOrder = true" label="Import purchase order(s)"></q-btn>
              <div v-if="fields.purchase_orders && fields.purchase_orders.length > 0">
                <q-input dense v-model="fields.purchase_order_numbers" disable label="Purchase Order(s)"></q-input>
              </div>
              <q-dialog v-model="importPurchaseOrder">
                <q-card style="min-width: min(60vw, 400px)">
                  <q-card-section class="bg-grey-4">
                    <div class="text-h6">
                      <span>Add Reference Purchase Order(s)</span>
                    </div>
                  </q-card-section>

                  <q-card-section class="q-mx-lg">
                    <q-input v-model.number="referenceFormData.invoice_no" label="Purchase Order No.*" autofocus type="number"></q-input>
                    <q-select class="q-mt-md" label="Fiscal Year" v-model="referenceFormData.fiscal_year"
                      :options="formDefaults.options.fiscal_years" option-value="id" option-label="name" map-options
                      emit-value></q-select>
                    <div class="row justify-end q-mt-lg">
                      <q-btn color="green" label="Add" size="md" @click="fetchInvoice()"></q-btn>
                    </div>
                  </q-card-section>
                </q-card>
              </q-dialog>
            </div>
            <div class="col-md-6 col-12">
              <n-auto-complete v-model="fields.party" :options="formDefaults.collections?.parties" label="Party"
                :error="errors?.party ? errors?.party : null"
                :modal-component="checkPermissions('PartyCreate') ? PartyForm : null" />
            </div>
            <q-input class="col-md-6 col-12" label="Bill No.*" v-model="fields.voucher_no"
              :error-message="errors.voucher_no" :error="!!errors.voucher_no">
            </q-input>
            <div class="col-md-6 col-12 row q-col-gutter-md">
              <div :class="['Percent', 'Amount'].includes(fields.discount_type)
                ? 'col-6'
                : 'col-12'
                ">
                <n-auto-complete v-model="fields.discount_type" label="Discount" :error="errors.discount_type"
                  :error-message="errors.discount_type" :options="formDefaults.collections
                    ? staticOptions.discount_types.concat(
                      formDefaults?.collections.discounts
                    )
                    : staticOptions.discount_types
                    " :modal-component="checkPermissions('PurchaseDiscountCreate') ? PurchaseDiscountForm : null">
                </n-auto-complete>
              </div>
              <div class="col-6 row">
                <div :class="formDefaults.options?.show_trade_discount_in_voucher
                  ? 'col-6'
                  : 'col-12'
                  " v-if="fields.discount_type === 'Amount' ||
    fields.discount_type === 'Percent'
    ">
                  <q-input class="col-6" v-model.number="fields.discount" label="Discount"
                    :error-message="errors.discount" :error="!!errors.discount"></q-input>
                </div>
                <div class="col-3 row" v-if="formDefaults.options?.show_trade_discount_in_voucher &&
                  ['Percent', 'Amount'].includes(fields.discount_type)
                  ">
                  <q-checkbox v-model="fields.trade_discount" label="Trade Discount?"></q-checkbox>
                </div>
              </div>
            </div>
            <div class="col-md-6 col-12">
              <date-picker v-model="fields.date" label="Date *" :error-message="errors.date"
                :error="!!errors.date"></date-picker>
            </div>
          </div>

          <div class="row q-col-gutter-md">
            <q-select v-model="fields.mode" label="Mode" class="col-12 col-md-6" :error-message="errors.mode"
              :error="!!errors.mode" :options="staticOptions.modes.concat(
                formDefaults.collections?.bank_accounts
              )
                " option-value="id" option-label="name" map-options emit-value>
              <template v-slot:append>
                <q-icon v-if="fields.mode !== null" class="cursor-pointer" name="clear"
                  @click.stop.prevent="fields.mode = null" /></template></q-select>
            <date-picker v-if="formDefaults.options?.enable_due_date_in_voucher" label="Due Date"
              v-model="fields.due_date" class="col-md-6 col-12" :error-message="errors?.due_date"
              :error="!!errors?.due_date" :toLimit="fields.date"></date-picker>
          </div>
          <!-- {{ fields.date }} -->
        </q-card-section>
      </q-card>
      <invoice-table :itemOptions="formDefaults.collections ? formDefaults.collections.items : null
        " :unitOptions="formDefaults.collections ? formDefaults.collections.units : null
    " :discountOptions="formDefaults.collections
    ? staticOptions.discount_types.concat(
      formDefaults?.collections.discounts
    )
    : staticOptions.discount_types
    " :taxOptions="formDefaults.collections?.tax_schemes" v-model="fields.rows" :mainDiscount="{
    discount_type: fields.discount_type,
    discount: fields.discount,
  }" :errors="!!errors.rows ? errors.rows : null" @deleteRowErr="(index, deleteObj) => deleteRowErr(index, errors, deleteObj)
  " :enableRowDescription="formDefaults.options?.enable_row_description"
        :showRowTradeDiscount="formDefaults.options?.show_trade_discount_in_row"></invoice-table>
      <div class="row q-px-lg">
        <div class="col-12 col-md-6 row">
          <!-- <q-input
            v-model="fields.remarks"
            label="Remarks"
            type="textarea"
          ></q-input> -->
          <q-input v-model="fields.remarks" label="Remarks" type="textarea" autogrow class="col-12 col-md-10"
            :error="!!errors?.remarks" :error-message="errors?.remarks" />
        </div>
        <div class="col-12 col-md-6 row justify-between">
          <div>
            <q-checkbox label="Import?" v-model="fields.is_import" class="q-mt-md col-3"></q-checkbox>
          </div>
          <!-- TODO: add sales agent form -->
        </div>
      </div>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn v-if="checkPermissions('PurchaseVoucherCreate') && !isEdit" :loading="loading"
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" color="orange" label="Draft" type="submit" />
        <q-btn v-if="checkPermissions('PurchaseVoucherCreate') && isEdit && fields.status === 'Draft'" :loading="loading"
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)" color="orange" label="Save Draft"
          type="submit" />
        <q-btn v-if="checkPermissions('PurchaseVoucherCreate') && !isEdit" :loading="loading"
          @click.prevent="() => onSubmitClick('Issued', fields, submitForm)" color="green" label="Issue" />
        <q-btn v-if="checkPermissions('PurchaseVoucherCreate') && isEdit" :loading="loading"
          @click.prevent="() => onSubmitClick('Issued', fields, submitForm)" color="green" label="Update" />
      </div>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import CategoryForm from '/src/pages/account/category/CategoryForm.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import PurchaseDiscountForm from 'src/pages/purchase/discounts/PurchaseDiscountForm.vue'
import InvoiceTable from 'src/components/voucher/InvoiceTable.vue'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const endpoint = '/v1/purchase-vouchers/'
    const openDatePicker = ref(false)
    const $q = useQuasar()
    const staticOptions = {
      discount_types: discount_types,
      modes: modes,
    }
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/purchase-voucher/list/',
    })
    const importPurchaseOrder = ref(false)
    const referenceFormData = ref({
      invoice_no: null,
      fiscal_year: null,
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value
            ? 'Update Purchases/Expenses'
            : 'Add Purchases/Expenses') + ' | Awecount',
      }
    })
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
      formData.fields.value.status = status
      try { await submitForm() } catch (err) {
        formData.fields.value.status = originalStatus
      }
    }
    formData.fields.value.date = formData.today
    formData.fields.value.due_date = formData.today
    formData.fields.value.is_import = false
    watch(() => formData.formDefaults.value, () => {
      if (!formData.isEdit.value) {
        if (formData.formDefaults.value.fields?.mode) {
          if (isNaN(formData.formDefaults.value.fields?.mode)) {
            formData.fields.value.mode = formData.formDefaults.value.fields.mode
          } else {
            formData.fields.value.mode = Number(formData.formDefaults.value.fields.mode)
          }
        } else formData.fields.value.mode = 'Credit'
      }
    })
    const fetchInvoice = async (data) => {
      const fetchData = data || { invoice_no: referenceFormData.value.invoice_no, fiscal_year: referenceFormData.value.fiscal_year }
      if (
        fetchData.invoice_no &&
        fetchData.fiscal_year
      ) {
        if (
          formData.fields.value.purchase_orders &&
          formData.fields.value.purchase_orders.includes(fetchData.invoice_no)
        ) {
          $q.notify({
            color: 'red-6',
            message: 'Invoice Already Exists!',
            icon: 'report_problem',
            position: 'top-right',
          })
        } else {
          const url = 'v1/purchase-order/by-voucher-no/'
          useApi(
            url +
            `?invoice_no=${fetchData.invoice_no}&fiscal_year=${fetchData.fiscal_year}`
          )
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
              } else formData.fields.value.purchase_orders = [data.id]
              if (formData.fields.value.purchase_order_numbers) {
                formData.fields.value.purchase_order_numbers.push(response.voucher_no)
              } else formData.fields.value.purchase_order_numbers = [response.voucher_no]
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
                'voucher_no'
              ]
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
              $q.notify({
                color: 'red-6',
                message: err.data?.detail || 'Error',
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
      }
    }
    onMounted(() => {
      const route = useRoute()
      if (route.query.purchase_order && route.query.fiscal_year) {
        const data = { invoice_no: route.query.purchase_order, fiscal_year: route.query.fiscal_year }
        fetchInvoice(data)
      }
    })
    watch(() => formData.formDefaults.value, () => {
      if (formData.formDefaults.value.fields?.hasOwnProperty('trade_discount')) {
        formData.fields.value.trade_discount = formData.formDefaults.value.fields?.trade_discount
      }
    })
    return {
      ...formData,
      CategoryForm,
      PartyForm,
      PurchaseDiscountForm,
      openDatePicker,
      staticOptions,
      InvoiceTable,
      deleteRowErr,
      onSubmitClick,
      checkPermissions,
      importPurchaseOrder,
      referenceFormData,
      fetchInvoice
    }
  },
}
</script>
