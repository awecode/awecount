<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Challan</span>
          <span v-else>Update Challan</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <div class="row">
                <div class="col-10">
                  <q-input
                    v-model="fields.customer_name"
                    label="Customer Name"
                    :error-message="errors.customer_name"
                    :error="!!errors.customer_name"
                    v-if="partyMode"
                  >
                  </q-input>
                  <n-auto-complete
                    v-else
                    v-model="fields.party"
                    :options="formDefaults.collections?.parties"
                    label="Party"
                    :error="errors?.party ? errors?.party : null"
                    :modal-component="PartyForm"
                  />
                </div>
                <div class="col-2 row justify-center q-py-md">
                  <q-btn flat size="md" @click="() => (partyMode = !partyMode)">
                    <q-icon name="mdi-account-group"></q-icon>
                  </q-btn>
                </div>
              </div>
              <div></div>
            </div>
            <q-input
              class="col-md-6 col-12"
              label="Deposit Date*"
              v-model="fields.date"
              disable
            >
            </q-input>
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.address"
              class="col-md-6 col-12"
              label="Address"
              :error-message="errors.address"
              :error="!!errors.address"
            ></q-input>
          </div>
        </q-card-section>
      </q-card>
      <invoice-table
        :itemOptions="
          formDefaults.collections ? formDefaults.collections.items : null
        "
        :unitOptions="
          formDefaults.collections ? formDefaults.collections.units : null
        "
        :discountOptions="
          formDefaults.collections
            ? staticOptions.discount_types.concat(
                formDefaults?.collections.discounts
              )
            : staticOptions.discount_types
        "
        :taxOptions="formDefaults.collections?.tax_schemes"
        v-model="fields.rows"
        :mainDiscount="{
          discount_type: fields.discount_type,
          discount: fields.discount,
        }"
        :errors="!!errors.rows ? errors.rows : null"
        @deleteRowErr="(index) => deleteRowErr(index, errors)"
        :disableExpand="true"
      ></invoice-table>
      <div class="row q-px-lg">
        <div class="col-12 col-md-6 row">
          <!-- <q-input
            v-model="fields.remarks"
            label="Remarks"
            type="textarea"
          ></q-input> -->
          <q-input
            v-model="fields.remarks"
            label="Remarks"
            type="textarea"
            autogrow
            class="col-12 col-md-10"
            :error="!!errors?.remarks"
            :error-message="errors?.remarks"
          />
        </div>
        <div class="col-12 col-md-6 row justify-between">
          <div>
            <q-checkbox
              label="Export?"
              v-model="fields.is_export"
              class="q-mt-md col-3"
            ></q-checkbox>
          </div>
          <q-select
            v-model="fields.sales_agent"
            label="Sales Agent"
            class="col-8"
            :error="!!errors?.sales_agent"
            :error-message="errors?.sales_agent"
          ></q-select>
          <!-- TODO: add sales agent form -->
        </div>
      </div>

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)"
          color="primary"
          label="Draft"
        />
        <q-btn
          @click.prevent="() => onSubmitClick('Issued', fields, submitForm)"
          color="green-8"
          :label="isEdit ? 'Update' : 'Issue'"
        />
      </div>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import CategoryForm from '/src/pages/account/category/CategoryForm.vue'
import PartyForm from 'src/pages/party/PartyForm.vue'
import SalesDiscountForm from 'src/pages/sales/discount/SalesDiscountForm.vue'
import InvoiceTable from 'src/components/voucher/InvoiceTable.vue'
import { discount_types, modes } from 'src/helpers/constants/invoice'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const endpoint = '/v1/sales-voucher/'
    const openDatePicker = ref(false)
    const $q = useQuasar()
    const staticOptions = {
      discount_types: discount_types,
      modes: modes,
    }
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/account/',
    })
    const partyMode = ref(false)
    const switchMode = (fields) => {
      if (fields.mode !== 'Credit') {
        partyMode.value = !partyMode.value
      } else
        $q.notify({
          color: 'orange-4',
          message: 'Credit customer must be a party!',
        })
    }
    const deleteRowErr = (index, errors) => {
      errors.rows.splice(index, 1)
    }
    const onSubmitClick = (status, fields, submitForm) => {
      fields.status = status
      submitForm()
    }
    formData.fields.value.date = formData.today
    formData.fields.value.is_export = false
    formData.fields.value.mode = 'Credit'
    formData.fields.value.party = ''
    return {
      ...formData,
      CategoryForm,
      PartyForm,
      SalesDiscountForm,
      openDatePicker,
      staticOptions,
      InvoiceTable,
      partyMode,
      switchMode,
      deleteRowErr,
      onSubmitClick,
    }
  },
}
</script>
