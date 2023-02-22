<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Sales Invoice | Draft</span>
          <span v-else>Update Account</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <n-auto-complete
                v-model="fields.party"
                :options="formDefaults.collections?.parties"
                label="Party"
                :error="errors?.party"
                :modal-component="PartyForm"
              />
            </div>
            <q-input
              class="col-md-6 col-12"
              label="Deposit Date*"
              v-model="fields.date"
              disable
            >
              <!-- <template v-slot:append>
                              <q-icon name="event" class="cursor-pointer">
                                <q-popup-proxy
                                  cover
                                  transition-show="scale"
                                  transition-hide="scale"
                                >
                                  <q-date v-model="fields.date" today-btn mask="YYYY-MM-DD">
                                    <div class="row items-center justify-end">
                                      <q-btn v-close-popup label="Close" flat />
                                    </div>
                                  </q-date>
                                </q-popup-proxy>
                              </q-icon>
                            </template> -->
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
            <div class="col-md-6 col-12 row q-col-gutter-md">
              <!-- <q-input
                              v-model="fields.discount_types"
                              label="Discount*"
                              :error-message="errors.discount_types"
                              :error="!!errors.discount_types"
                            ></q-input> -->
              <div class="col-grow">
                <n-auto-complete
                  v-model="fields.discount_type"
                  label="Discount*"
                  :error="errors?.discount_types"
                  :options="
                    formDefaults.collections
                      ? options.discount_types.concat(
                          formDefaults?.collections.discounts
                        )
                      : options.discount_types
                  "
                  :modal-component="SalesDiscountForm"
                >
                </n-auto-complete>
              </div>
              <div
                class="col-3"
                v-if="
                  fields.discount_type === 'Amount' ||
                  fields.discount_type === 'Percent'
                "
              >
                <q-input
                  v-model="fields.discount"
                  label="Discount"
                  :error-message="errors.discount"
                  :error="!!errors.discount"
                ></q-input>
              </div>
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <q-select
              v-model="fields.mode"
              label="Mode"
              class="col-12 col-md-6"
              :error-message="errors.bank_account"
              :error="!!errors.bank_account"
              :options="formDefaults.collections?.bank_accounts"
              option-value="value"
              option-label="id"
              map-options
              emit-value
            >
              <template v-slot:append>
                <q-icon
                  v-if="fields.mode !== null"
                  class="cursor-pointer"
                  name="clear"
                  @click.stop.prevent="fields.mode = null" /></template
            ></q-select>
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
            ? options.discount_types.concat(formDefaults?.collections.discounts)
            : options.discount_types
        "
        :taxOptions="formDefaults.collections?.tax_schemes"
        v-model="fields.rows"
        :mainDiscount="{
          discount_type: fields.discount_type,
          discount: fields.discount,
        }"
      ></invoice-table>
      <div class="text-right q-pr-md q-pb-lg">
        <q-btn
          @click.prevent="submitForm"
          color="primary"
          :label="isEdit ? 'Update' : 'Create'"
          class="q-ml-auto"
        />
      </div>
    </q-card>
    {{ fields.discount_type }}--row
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
  setup(props, context) {
    const endpoint = '/v1/sales-voucher/'
    const openDatePicker = ref(false)
    const rows = ref(1)
    const options = {
      discount_types: discount_types,
      modes: modes,
      // show_customer: true,
      // challan_objs: [],
    }
    // const mainDiscountComputed = computed(() => {
    //   let obj = null
    //   console.log(fields.value.discount_type, 'distype')
    //   return obj
    // })
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/account/',
    })
    formData.fields.value.date = formData.today
    return {
      ...formData,
      CategoryForm,
      PartyForm,
      SalesDiscountForm,
      openDatePicker,
      options,
      rows,
      InvoiceTable,
    }
  },
}
</script>
