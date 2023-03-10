<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Payment Receipt</span>
          <span v-else>Update Payment Receipt</span>
        </div>
      </q-card-section>
      <q-separator inset />

      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row">
            <div class="col-md-6 col-12 row q-col-gutter-md">
              <span style="flex-grow: 1"
                ><q-input label="For Invoice(s)" disabled="true"> </q-input
              ></span>
              <span
                class="row items-center"
                style="flex-grow: 0; flex-shrink: 0"
                ><q-btn
                  icon="add"
                  color="blue"
                  @click="() => (addInoviceModal = !addInoviceModal)"
                >
                </q-btn
              ></span>
            </div>
            <!-- <q-input
              class="col-md-6 col-12"
              label="Deposit Date*"
              v-model="fields.date"
            >
            </q-input> -->
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              class="col-md-6 col-12"
              label="Deposit Date*"
              v-model="fields.date"
            ></q-input>
            <q-select
              v-model="fields.mode"
              label="Mode"
              class="col-12 col-md-6"
              :error-message="errors.mode"
              :error="!!errors.mode"
              :options="['Cheque', 'Cash', 'Bank Deposit']"
            ></q-select>
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              class="col-md-6 col-12"
              label="Amount"
              type="number"
              v-model="fields.amount"
              :error-message="errors.amount"
              :error="!!errors.amount"
            ></q-input>
            <q-input
              class="col-md-6 col-12"
              label="TDS Amount"
              v-model="fields.tds_amount"
              :error-message="errors.tds_amount"
              :error="!!errors.tds_amount"
              type="number"
            ></q-input>
          </div>
          <div
            v-if="fields.mode === 'Bank Deposit' || fields.mode === 'Cheque'"
            class="row q-col-gutter-md"
          >
            <q-select
              class="col-md-6 col-12"
              label="Bank Accounts"
              v-model="fields.bank_account"
              :error-message="errors.bank_account"
              :error="!!errors.bank_account"
              :options="formDefaults.collections?.bank_accounts"
              option-value="id"
              option-label="name"
              map-options
              emit-value
            ></q-select>
          </div>
          <div v-if="fields.mode === 'Cheque'">
            <div class="row q-col-gutter-md">
              <q-input
                class="col-md-6 col-12"
                label="Cheque Date"
                v-model="fields.cheque_date"
                :error-message="errors.cheque_date"
                :error="!!errors.cheque_date"
                type="date"
                placeholder=""
              ></q-input>
              <q-input
                class="col-md-6 col-12"
                label="Cheque Number"
                v-model="fields.cheque_number"
                :error-message="errors.cheque_number"
                :error="!!errors.cheque_number"
                type="number"
              ></q-input>
            </div>
            <q-input
              v-model="fields.drawee_bank"
              label="Drawee Bank"
              type="textarea"
              autogrow
              class="col-12 col-md-10"
              :error="!!errors?.drawee_bank"
              :error-message="errors?.drawee_bank"
            />
          </div>
          <q-input
            v-model="fields.remarks"
            label="Remarks"
            type="textarea"
            autogrow
            class="col-12 col-md-10"
            :error="!!errors?.remarks"
            :error-message="errors?.remarks"
          />
        </q-card-section>
      </q-card>
      <div class="q-ma-md row q-pb-lg">
        <q-btn
          @click.prevent="() => onSubmitClick('Draft', fields, submitForm)"
          color="green-8"
          :label="isEdit ? 'Update' : 'Create'"
        />
      </div>
    </q-card>
    <q-dialog v-model="addInoviceModal">
      <q-card style="min-width: min(40vw, 500px)">
        <q-card-section class="bg-grey-4">
          <div class="text-h6">
            <span class="q-mx-md">Add Invoice</span>
          </div>
        </q-card-section>
        <q-separator inset />
        <q-card-section class="q-mb-md">
          <div class="text-right q-mt-lg row justify-between q-mx-md">
            <q-input label="Invoice No.*" class="col-12"> </q-input>
          </div>
          <div class="row q-mt-lg justify-end">
            <q-btn label="update" color="orange-5" class="q-mt-md"></q-btn>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, { emit }) {
    const endpoint = '/v1/payment-receipt/'
    const openDatePicker = ref(false)
    const addInoviceModal = ref(false)
    const invoiceFormData = ref({
      fiscal_year: null,
      invoice_no: null,
    })
    // const $q = useQuasar()
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/payment-receipt/list/',
    })
    const onSubmitClick = (status, fields, submitForm) => {
      fields.status = status
      submitForm()
    }
    // const switchPartyMode = (fields, isEdit) => {
    //   if (isEdit && !!fields.customer_name) {
    //     fields.customer_name = null
    //     partyMode.value = true
    //   } else {
    //     if (partyMode.value) {
    //       fields.party_name = null
    //       fields.party = null
    //     } else {
    //       fields.customer_name = null
    //     }
    //     partyMode.value = !partyMode.value
    //   }
    // }
    formData.fields.value.date = formData.today
    formData.fields.value.mode = 'Cheque'
    // watch(
    //   () => formData.fields.value.party,
    //   (newValue) => {
    //     if (newValue) {
    //       const index =
    //         formData.formDefaults.value.collections.parties.findIndex(
    //           (option) => option.id === newValue
    //         )
    //       formData.fields.value.address =
    //         formData.formDefaults.value.collections.parties[index].address
    //       // const index = formDefaults.
    //     }
    //   }
    // )
    return {
      ...formData,
      onSubmitClick,
      addInoviceModal,
      invoiceFormData,
    }
  },
  // onmounted: () => console.log('mounted'),
}
</script>
