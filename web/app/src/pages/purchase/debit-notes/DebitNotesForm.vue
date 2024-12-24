<script>
import InvoiceTable from 'src/components/voucher/InvoiceTable.vue'
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'
import { discount_types, modes } from 'src/helpers/constants/invoice'
import CategoryForm from 'src/pages/account/category/CategoryForm.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import PurchaseDiscountForm from 'src/pages/purchase/discounts/PurchaseDiscountForm.vue'
import { useLoginStore } from 'src/stores/login-info'

export default {
  setup() {
    const route = useRoute()
    const store = useLoginStore()
    const endpoint = `/api/company/${route.params.company}/debit-note/`
    const openDatePicker = ref(false)
    const addRefrence = ref(false)
    const discountField = ref(null)
    const partyChoices = ref(null)
    const referenceFormData = ref({
      invoice_no: null,
      fiscal_year: store.companyInfo?.current_fiscal_year_id || null,
    })
    const $q = useQuasar()
    const staticOptions = {
      discount_types,
      modes,
    }
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/debit-note/list/',
    })
    useMeta(() => {
      return {
        title:
          `${formData.isEdit?.value ? 'Debit Notes Update' : 'Debit Notes Add'
          } | Awecount`,
      }
    })
    const partyMode = ref(false)
    const switchMode = (fields) => {
      if (fields.payment_mode) {
        partyMode.value = !partyMode.value
      } else {
        $q.notify({
          color: 'orange-4',
          message: 'Credit customer must be a party!',
        })
      }
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
      const data = await formData.submitForm()
      if (data && data.hasOwnProperty('error')) {
        formData.fields.value.status = originalStatus
      }
    }
    const fetchInvoice = (fields) => {
      if (!formData?.errors?.value) formData.errors.value = {}
      delete formData.errors.value.fiscal_year
      delete formData.errors.value.invoice_no
      delete formData.errors.value.party
      if (
        referenceFormData.value.invoice_no
        && referenceFormData.value.fiscal_year
        && referenceFormData.value.party
      ) {
        const url = 'v1/purchase-vouchers/by-voucher-no/'
        useApi(
          `${url
          }?invoice_no=${referenceFormData.value.invoice_no}&fiscal_year=${referenceFormData.value.fiscal_year}&party=${referenceFormData.value.party}`,
        )
          .then((data) => {
            if (fields.invoices) {
              fields.invoices.push(data.id)
            } else {
              fields.invoices = [data.id]
            }
            fields.invoice_data = [{
              id: data.id,
              voucher_no: data.voucher_no,
            }]
            const removeArr = [
              'id',
              'date',
              'voucher_meta',
              'print_count',
              'issue_datetime',
              'is_export',
              'status',
              'due_date',
              'date',
              'remarks',
            ]
            removeArr.forEach((item) => {
              delete data[item]
            })
            data.rows.forEach((row) => {
              row.taxObj = row.tax_scheme
              if (row.discount_type === '') {
                row.discount_type = null
              }
            })
            for (const key in data) {
              fields[key] = data[key]
              // if (key === )
            }
            if (data.discount_obj && data.discount_obj.id) {
              fields.discount_type = data.discount_obj.id
            }
            addRefrence.value = false
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
      } else {
        if (!referenceFormData.value.invoice_no) {
          formData.errors.value.invoice_no = 'Invoice Number is required!'
        }
        if (!referenceFormData.value.party) {
          formData.errors.value.party = 'Party is required!'
        }
        if (!referenceFormData.value.fiscal_year) {
          formData.errors.value.fiscal_year = 'Fiscal Year is required!'
        }
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
    formData.fields.value.payment_mode = null
    formData.fields.value.party = ''
    formData.fields.value.discount_type = null
    formData.fields.value.trade_discount = false

    // to update voucher meta in Credit and debit Notes
    const updateVoucherMeta = (data) => {
      // formData.fields.value.discount = data.discount
      formData.fields.value.meta_discount = data.discount
      formData.fields.value.meta_sub_total = data.subTotal
      formData.fields.value.meta_tax = data.totalTax
      formData.fields.value.total_amount = data.total
    }
    const discountOptionsComputed = computed(() => {
      if (formData?.formDefaults.value?.collections?.discounts) {
        return staticOptions.discount_types.concat(
          formData.formDefaults.value.collections.discounts,
        )
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
      InvoiceTable,
      partyMode,
      switchMode,
      deleteRowErr,
      onSubmitClick,
      addRefrence,
      fetchInvoice,
      referenceFormData,
      discountField,
      partyChoices,
      checkPermissions,
      updateVoucherMeta,
      discountOptionsComputed,
      modeOptionsComputed,
    }
  },
  created() {
    useApi(`/api/company/${this.$route.params.company}/parties/choices/`)
      .then((res) => {
        this.partyChoices = res
      })
      .catch((err) => {
        console.log('error fetching choices due to', err)
      })
  },
}
</script>

<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Debit Note | Draft</span>
          <span v-else>Update Debit Note</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div v-if="fields.invoice_data && fields.invoice_data.length > 0" class="col-md-6 col-12">
              <q-input v-model="fields.invoice_data[0].voucher_no" disable label="Reference Invoice(s)" />
            </div>
            <div v-else class="col-md-6 col-12">
              <q-btn color="blue" label="Add Refrence" @click="() => (addRefrence = true)" />
              <q-dialog v-model="addRefrence" @before-hide="errors && delete errors?.fiscal_year && delete errors?.invoice_no && delete errors?.party">
                <q-card style="min-width: min(60vw, 400px)">
                  <q-card-section class="bg-grey-4 flex justify-between">
                    <div class="text-h6">
                      <span>Add Reference Invoice(s)</span>
                    </div>
                    <q-btn v-close-popup icon="close" class="text-white bg-red-500 opacity-95" flat round dense />
                  </q-card-section>
                  <q-card-section class="q-mx-lg">
                    <q-input v-model="referenceFormData.invoice_no" class="mb-4" label="Invoice No.*" autofocus type="text" :error="!!errors?.invoice_no" :error-message="errors?.invoice_no" />
                    <n-auto-complete-v2
                      v-model="referenceFormData.party"
                      label="Party*"
                      :options="partyChoices"
                      :error="errors?.party"
                      :endpoint="`/api/company/${$route.params.company}/parties/choices/`"
                    />
                    <!-- <q-select class="q-mt-md" label="Party*" v-model="referenceFormData.party" :options="partyChoices"
                      option-value="id" option-label="name" map-options emit-value></q-select> -->
                    <q-select
                      v-model="referenceFormData.fiscal_year"
                      label="Fiscal Year"
                      :options="formDefaults.options?.fiscal_years"
                      option-value="id"
                      option-label="name"
                      map-options
                      emit-value
                      :error="!!errors?.fiscal_year"
                      :error-message="errors?.fiscal_year"
                    />
                    <div class="row justify-end q-mt-lg">
                      <q-btn color="green" label="Add" size="md" @click="() => fetchInvoice(fields)" />
                    </div>
                  </q-card-section>
                </q-card>
              </q-dialog>
            </div>
            <date-picker v-model="fields.date" class="col-md-6 col-12" label="Start Date *" :error="!!errors?.date" :error-message="errors?.date" />
          </div>
          <div class="row q-col-gutter-xl">
            <div class="col-md-6 col-12 row q-col-gutter-md">
              <div
                :class="fields.discount_type === 'Amount'
                  || fields.discount_type === 'Percent'
                  ? 'col-4'
                  : 'col-12'
                "
              >
                <n-auto-complete v-model="fields.discount_type" label="Discount" :error="errors?.discount" :options="discountOptionsComputed" :modal-component="checkPermissions('purchasediscount.create') ? PurchaseDiscountForm : null" />
              </div>
              <div
                v-if="fields.discount_type === 'Amount'
                  || fields.discount_type === 'Percent'
                "
                class="col-8 row"
              >
                <q-input
                  v-model.number="fields.discount"
                  class="col-6"
                  label="Discount"
                  :error-message="errors?.discount"
                  :error="!!errors?.discount"
                />
                <q-checkbox v-model="fields.trade_discount" label="Trade Discount?" class="col-6" />
              </div>
            </div>
            <div class="col-md-6 col-12">
              <n-auto-complete-v2
                v-model="fields.payment_mode"
                label="Payment Mode *"
                :error-message="errors?.payment_mode"
                :error="!!errors?.payment_mode"
                :options="modeOptionsComputed"
                :endpoint="`/api/company/${$route.params.company}/debit-note/create-defaults/payment_modes`"
                :static-option="isEdit ? fields.selected_payment_mode_obj : formDefaults.options?.default_payment_mode_obj"
                option-value="id"
                option-label="name"
                map-options
                emit-value
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
          </div>
        </q-card-section>
      </q-card>
      <invoice-table
        v-if="formDefaults.collections"
        v-model="fields.rows"
        :item-options="formDefaults.collections ? formDefaults.collections.items : null
        "
        :unit-options="formDefaults.collections ? formDefaults.collections.units : null
        "
        :discount-options="discountOptionsComputed"
        :tax-options="formDefaults.collections?.tax_schemes"
        :main-discount="{
          discount_type: fields.discount_type,
          discount: fields.discount,
        }"
        :errors="!!errors?.rows ? errors?.rows : null"
        used-in="creditNote"
        @delete-row-err="(index) => deleteRowErr(index, errors, deleteObj)"
        @update-voucher-meta="updateVoucherMeta"
      />
      <div class="row q-px-lg">
        <q-input
          v-model="fields.remarks"
          label="Remarks"
          type="textarea"
          autogrow
          class="col-12"
          :error="!!errors?.remarks"
          :error-message="errors?.remarks"
        />
      </div>
      <div
        v-if="checkPermissions('debitnote.create')"
        class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md"
      >
        <q-btn
          v-if="!isEdit"
          :loading="loading"
          :disabled="!(fields.invoices && fields.invoices.length > 0)"
          color="orange"
          label="Save Draft"
          :disable="fields.invoices ? false : true"
          type="submit"
          @click.prevent="() => onSubmitClick('Draft')"
        />
        <q-btn
          v-if="isEdit && fields.status === 'Draft'"
          :loading="loading"
          :disabled="!(fields.invoices && fields.invoices.length > 0)"
          color="orange"
          label="Update Draft"
          :disable="fields.invoices ? false : true"
          type="submit"
          @click.prevent="() => onSubmitClick('Draft')"
        />
        <q-btn
          :loading="loading"
          color="green"
          :label="isEdit ? fields?.status === 'Draft' ? 'Issue from Draft' : 'Update' : 'Issue'"
          :disabled="!(fields.invoice_data && fields.invoice_data.length > 0)"
          @click.prevent="() => onSubmitClick(isEdit ? fields.status === 'Draft' ? 'Issued' : fields.status : 'Issued')"
        />
      </div>
    </q-card>
  </q-form>
</template>
