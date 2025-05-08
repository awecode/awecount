<script setup lang="ts">
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'
import { discount_types } from 'src/helpers/constants/invoice'
import { useLoginStore } from 'src/stores/login-info'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const endpoint = `/api/company/${route.params.company}/quotation/`

const { fields, formDefaults, errors, isEdit, loading, submitForm } = useForm(endpoint, {
  getDefaults: true,
  successRoute: `/${route.params.company}/sales/quotations`,
})

useMeta(() => ({
  title: `${isEdit.value ? 'Quotation Update' : 'Quotation Add'} | Awecount`,
}))

const router = useRouter()

const customerMode = ref(false)

const onSubmitClick = async (status, redirect) => {
  const originalStatus = fields.value.status
  fields.value.status = status

  const taxType = fields.value.tax_type
  // if fields has tax_type as tax_inclusive then decrease the tax_amount from the total amount
  // find

  if (taxType === 'tax_inclusive') {
    fields.value.rows.forEach((row) => {
      if (row.tax_scheme_id) {
        const taxObj = formDefaults.value.value.collections.tax_schemes.results.find(tax => tax.id === row.tax_scheme_id)
        row.rate = Number((row.rate / (1 + taxObj.rate / 100)).toFixed(6))
      }
    })
  }

  const data = await submitForm()
  if (data && data.hasOwnProperty('error')) {
    fields.value.status = originalStatus
  } else if (redirect) {
    router.push({
      name: 'company-sales-quotations-id',
      params: {
        company: route.params.company,
        id: data.id,
      },
      query: {
        print: true,
      },
    })
  }
}

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

const importChallanModal = ref(false)

const loginStore = useLoginStore()

const aliases = ref([])

const $q = useQuasar()

const referenceFormData = ref({
  invoice_no: null,
  fiscal_year: loginStore.companyInfo.current_fiscal_year_id || null,
})

const onPartyChange = (obj) => {
  if (obj) {
    fields.value.address = obj.address
    if (obj.aliases && obj.aliases.length > 0) {
      aliases.value = [{ name: obj.name, id: null }, ...obj.aliases.map(item => ({ name: item, id: item }))]
    }
  }
}

const staticOptions = {
  discount_types,
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

watch(
  () => formDefaults.value,
  () => {
    if (formDefaults.value.fields?.hasOwnProperty('trade_discount')) {
      fields.value.trade_discount = formDefaults.value.fields?.trade_discount
    }
    if (isEdit.value) {
      if (fields.value.customer_name) customerMode.value = true
    } else {
      fields.value.is_export = false
    }
    fields.value.tax_type = fields.value.tax_type || 'tax_exclusive'
  },
)

// const switchMode = () => {
//   // customerMode.value = !customerMode.value
// }
</script>

<template>
  <q-form v-if="fields" autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6" data-testid="form-title">
          <span v-if="!isEdit">New Quotation | Draft</span>
          <span v-else>
            Update Quotation | {{ fields.status }}
            <span v-if="fields.number">| # {{ fields.number }}</span>
          </span>
        </div>
      </q-card-section>
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <div class="row">
                <div class="col-12">
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

                <!-- <div class="col-2 row justify-center q-py-md">
                  <q-btn
                    flat
                    data-testid="switch-account-group-btn"
                    size="md"
                    @click="() => switchMode(fields)"
                  >
                    <q-icon name="mdi-account-group" />
                  </q-btn>
                </div> -->
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

            <date-picker
              v-model="fields.date"
              class="col-md-6 col-12"
              label="Date*"
              :error="errors?.date ? errors?.date : null"
              :error-message="errors?.date"
            />

            <date-picker
              v-model="fields.expiry_date"
              class="col-md-6 col-12"
              label="Expiry Date"
              :error="errors?.expiry_date ? errors?.expiry_date : null"
              :error-message="errors?.expiry_date"
            />
            <q-input
              v-model="fields.address"
              class="col-md-6 col-12"
              data-testid="address-input"
              label="Address"
              :error="!!errors?.address"
              :error-message="errors?.address"
            />
            <div class="col-md-6 col-12 row q-col-gutter-md">
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

            <div class="col-12 col-md-6">
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
        :errors="errors?.rows ? errors.rows : null"
        :has-challan="false"
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
        <div class="col-12 col-md-6 row">
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
        <div class="col-12 col-md-6 row justify-between">
          <div class="col-3">
            <q-checkbox
              v-model="fields.is_export"
              class="q-mt-md col-3"
              data-testid="export-checkbox"
              label="Export?"
            />
          </div>
          <div class="col-9">
            <n-auto-complete-v2
              v-model="fields.sales_agent"
              class="col-8"
              data-testid="sales-agent-select"
              label="Sales Agent"
              :endpoint="`/api/company/${$route.params.company}/sales-voucher/create-defaults/sales_agents`"
              :error="errors?.sales_agent"
              :options="formDefaults.collections?.sales_agents"
              :static-option="fields.selected_sales_agent_obj"
            />
          </div>
        </div>
      </div>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn
          v-if="!isEdit && checkPermissions('quotations.create')"
          color="orange-8"
          data-testid="issue-btn"
          label="Save Draft"
          type="submit"
          :loading="loading"
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)"
        />

        <q-btn
          v-if="isEdit && fields.status === 'Draft' && checkPermissions('quotations.update')"
          color="orange-8"
          data-testid="draft-btn"
          type="submit"
          :label="isEdit ? 'Update Draft' : 'Save Draft'"
          :loading="loading"
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)"
        />

        <div v-if="checkPermissions('quotations.create')">
          <q-btn
            color="green"
            data-testid="create/update-btn"
            :label="
              isEdit
                ? fields?.status !== 'Draft' ? 'Update'
                  : fields?.status === 'Draft' ? `Generate # ${formDefaults.options?.number || 1} from Draft`
                    : 'update'
                : `Generate # ${formDefaults.options?.number || 1}`
            "
            :loading="loading"
            @click.prevent="
              () =>
                onSubmitClick(
                  isEdit
                    ? fields.status === 'Draft'
                      ? 'Generated'
                      : fields.status
                    : 'Generated',
                )
            "
          />
        </div>
      </div>
    </q-card>
  </q-form>
</template>
