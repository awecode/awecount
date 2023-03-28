<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Cheque Deposit</span>
          <span v-else>Update Cheque Deposit</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mt-none q-ml-lg q-mr-lg q-mb-lg">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <n-auto-complete
                v-model="fields.bank_account"
                :options="formDefaults.collections?.bank_accounts"
                label="Bank Account *"
                :modal-component="CreateAccount"
                :error="errors?.bank_account"
              />
            </div>
            <div class="col-md-6 col-12">
              <n-auto-complete
                v-model="fields.benefactor"
                :options="formDefaults.collections?.benefactors"
                label="Benefactor *"
                :modal-component="BenefactorForm"
                :error="errors?.benefactor"
              />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.amount"
              label="Amount *"
              class="col-md-6 col-12"
              :error-message="errors.amount"
              :error="!!errors.amount"
            />
            <date-picker
              v-model="fields.date"
              class="col-md-6 col-12"
              label="Deposit Date*"
              :error-message="errors.date"
              :error="!!errors.date"
            ></date-picker>
          </div>
          <div class="row q-col-gutter-md">
            <date-picker
              v-model="fields.cheque_date"
              class="col-md-6 col-12"
              label="Cheque Date"
              :error-message="errors.cheque_date"
              :error="!!errors.cheque_date"
            ></date-picker>
            <q-input
              v-model="fields.cheque_number"
              label="Cheque Number"
              class="col-6"
              :error-message="errors.cheque_number"
              :error="!!errors.cheque_number"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.voucher_no"
              label="Voucher Number"
              class="col-md-6 col-12"
              :error-message="errors.voucher_no"
              :error="!!errors.voucher_no"
            />
            <q-input
              v-model="fields.deposited_by"
              label="Deposited By"
              class="col-md-6 col-12"
              :error-message="errors.deposited_by"
              :error="!!errors.deposited_by"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.drawee_bank"
              label="Drawee Bank"
              class="col-md-6 col-12"
              :error-message="errors.drawee_bank"
              :error="!!errors.drawee_bank"
            />
          </div>
        </q-card-section>
      </q-card>
    </q-card>
    <div class="row q-mt-md">
      <q-btn
        v-if="fields.status == 'Draft' || !fields.status"
        @click.prevent=";(fields.status = 'Draft'), submitForm()"
        color="amber-7"
        icon="fa-solid fa-pen-to-square"
        label="Save Draft"
        class="q-mr-md q-py-sm"
      />
      <q-btn
        @click.prevent="
          fields.status
            ? fields.status == 'Draft'
              ? (fields.status = 'Issued')
              : ''
            : (fields.status = 'Issued'),
            submitForm()
        "
        color="green-6"
        icon="fa-solid fa-floppy-disk"
        :label="isEdit ? 'Update' : 'Issue'"
      />
    </div>
  </q-form>
</template>

<script>
import CreateAccount from '../account/AccountForm.vue'
import useForm from '/src/composables/useForm'
import BenefactorForm from '/src/components/BenefactorForm.vue'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/cheque-deposits/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/bank/cheque-deposit/',
    })

    formData.fields.value.cheque_date =
      formData.fields.value.cheque_date || formData.today

    formData.fields.value.date = formData.fields.value.date || formData.today
    return {
      ...formData,
      CreateAccount,
      BenefactorForm,
    }
  },
}
</script>
