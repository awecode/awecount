<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'
import BenefactorForm from 'src/pages/account/ledger/LedgerForm.vue'
import CreateAccount from '../account/AccountForm.vue'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/cheque-deposits/`
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/cheque-deposit/list/',
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Cheque Deposit Update' : 'Cheque Deposit Add'} | Awecount`,
      }
    })
    formData.fields.value.cheque_date = formData.fields.value.cheque_date || formData.today

    formData.fields.value.date = formData.fields.value.date || formData.today

    const onSubmitClick = async (status) => {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      const data = await formData.submitForm()
      if (data && data.hasOwnProperty('error')) {
        formData.fields.value.status = originalStatus
      }
    }
    return {
      ...formData,
      CreateAccount,
      BenefactorForm,
      checkPermissions,
      onSubmitClick,
    }
  },
}
</script>

<template>
  <q-form autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Cheque Deposit</span>
          <span v-else>Update Cheque Deposit</span>
        </div>
      </q-card-section>

      <q-card class="q-mt-none q-ml-lg q-mr-lg q-mb-lg">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <n-auto-complete-v2
                v-model="fields.bank_account"
                label="Bank Account *"
                :endpoint="`/api/company/${$route.params.company}/cheque-deposits/create-defaults/bank_accounts`"
                :error="errors?.bank_account"
                :modal-component="checkPermissions('bankaccount.create') ? CreateAccount : null"
                :options="formDefaults.collections?.bank_accounts"
                :static-option="fields.selected_bank_account_obj"
              />
            </div>
            <div class="col-md-6 col-12">
              <n-auto-complete-v2
                v-model="fields.benefactor"
                label="Benefactor *"
                :endpoint="`/api/company/${$route.params.company}/cheque-deposits/create-defaults/benefactors`"
                :error="errors?.benefactor"
                :modal-component="checkPermissions('account.create') ? BenefactorForm : null"
                :options="formDefaults.collections?.benefactors"
                :static-option="fields.selected_benefactor_obj"
              />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.amount"
              class="col-md-6 col-12"
              label="Amount *"
              type="number"
              :error="!!errors.amount"
              :error-message="errors.amount"
            />
            <date-picker
              v-model="fields.date"
              class="col-md-6 col-12"
              label="Deposit Date*"
              :error="!!errors.date"
              :error-message="errors.date"
            />
          </div>
          <div class="row q-col-gutter-md">
            <date-picker
              v-model="fields.cheque_date"
              class="col-md-6 col-12"
              label="Cheque Date"
              :error="!!errors.cheque_date"
              :error-message="errors.cheque_date"
              :not-required="true"
            />
            <q-input
              v-model="fields.cheque_number"
              class="col-md-6 col-12"
              label="Cheque Number"
              type="number"
              :error="!!errors.cheque_number"
              :error-message="errors.cheque_number"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.voucher_no"
              class="col-md-6 col-12"
              label="Voucher Number"
              type="number"
              :error="!!errors.voucher_no"
              :error-message="errors.voucher_no"
            />
            <q-input
              v-model="fields.deposited_by"
              class="col-md-6 col-12"
              label="Deposited By"
              :error="!!errors.deposited_by"
              :error-message="errors.deposited_by"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.drawee_bank"
              class="col-md-6 col-12"
              label="Drawee Bank"
              :error="!!errors.drawee_bank"
              :error-message="errors.drawee_bank"
            />
          </div>
        </q-card-section>
      </q-card>
    </q-card>
    <div class="row q-mt-md justify-end">
      <q-btn
        v-if="checkPermissions('chequedeposit.create') && !isEdit"
        class="q-mr-md q-py-sm"
        color="orange"
        icon="fa-solid fa-pen-to-square"
        label="Draft"
        type="submit"
        :loading="loading"
        @click.prevent="onSubmitClick('Draft')"
      />
      <q-btn
        v-if="checkPermissions('chequedeposit.create') && isEdit && fields?.status === 'Draft'"
        class="q-mr-md q-py-sm"
        color="orange"
        icon="fa-solid fa-pen-to-square"
        label="Save Draft"
        :loading="loading"
        @click.prevent="onSubmitClick('Draft')"
      />
      <q-btn
        v-if="checkPermissions('chequedeposit.create') && !isEdit"
        color="green-6"
        icon="fa-solid fa-floppy-disk"
        label="Issue"
        :loading="loading"
        @click.prevent="onSubmitClick('Issued')"
      />
      <q-btn
        v-if="checkPermissions('chequedeposit.modify') && isEdit"
        color="green-6"
        icon="fa-solid fa-floppy-disk"
        type="submit"
        :label="fields.status === 'Draft' ? 'Issue' : 'Update'"
        :loading="loading"
        @click.prevent="onSubmitClick(fields.status === 'Draft' ? 'Issued' : fields.status)"
      />
    </div>
  </q-form>
</template>
