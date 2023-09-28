<template>
  <q-form class="q-pa-lg" autofocus>
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
              <n-auto-complete v-model="fields.bank_account" :options="formDefaults.collections?.bank_accounts"
                label="Bank Account *" :modal-component="checkPermissions('BankAccountCreate') ? CreateAccount : null" :error="errors?.bank_account" />
            </div>
            <div class="col-md-6 col-12">
              <n-auto-complete v-model="fields.benefactor" :options="formDefaults.collections?.benefactors"
                label="Benefactor *" :modal-component="checkPermissions('AccountCreate') ? BenefactorForm : null" :error="errors?.benefactor" />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.amount" label="Amount *" class="col-md-6 col-12" :error-message="errors.amount"
              :error="!!errors.amount" type="number" />
            <date-picker v-model="fields.date" class="col-md-6 col-12" label="Deposit Date*" :error-message="errors.date"
              :error="!!errors.date"></date-picker>
          </div>
          <div class="row q-col-gutter-md">
            <date-picker v-model="fields.cheque_date" class="col-md-6 col-12" label="Cheque Date"
              :error-message="errors.cheque_date" :error="!!errors.cheque_date"></date-picker>
            <q-input v-model="fields.cheque_number" label="Cheque Number" class="col-6"
              :error-message="errors.cheque_number" :error="!!errors.cheque_number" type="number" />
          </div>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.voucher_no" label="Voucher Number" class="col-md-6 col-12"
              :error-message="errors.voucher_no" :error="!!errors.voucher_no" type="number" />
            <q-input v-model="fields.deposited_by" label="Deposited By" class="col-md-6 col-12"
              :error-message="errors.deposited_by" :error="!!errors.deposited_by" />
          </div>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.drawee_bank" label="Drawee Bank" class="col-md-6 col-12"
              :error-message="errors.drawee_bank" :error="!!errors.drawee_bank" />
          </div>
        </q-card-section>
      </q-card>
    </q-card>
    <div class="row q-mt-md justify-end">
      <q-btn v-if="checkPermissions('ChequeDepositCreate') && !isEdit"
        @click.prevent="onSubmitClick('Draft')" color="orange" icon="fa-solid fa-pen-to-square" :loading="loading"
        label="Draft" type="submit" class="q-mr-md q-py-sm" />
      <q-btn v-if="checkPermissions('ChequeDepositCreate') && isEdit && fields?.status === 'Draft'"
        @click.prevent="onSubmitClick('Draft')" color="orange" icon="fa-solid fa-pen-to-square" :loading="loading"
        label="Save Draft" class="q-mr-md q-py-sm" />
      <q-btn v-if="checkPermissions('ChequeDepositCreate') && !isEdit" @click.prevent="onSubmitClick('Issued')" color="green-6" icon="fa-solid fa-floppy-disk" label="Issue" :loading="loading" />
      <q-btn v-if="checkPermissions('ChequeDepositModify') && isEdit" @click.prevent="onSubmitClick('Issued')" color="green-6" icon="fa-solid fa-floppy-disk" label="Update" type="submit" :loading="loading"/>
    </div>
  </q-form>
</template>

<script>
import CreateAccount from '../account/AccountForm.vue'
import useForm from '/src/composables/useForm'
import BenefactorForm from 'src/pages/account/ledger/LedgerForm.vue'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/cheque-deposits/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/cheque-deposit/list/',
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value
            ? 'Cheque Deposit Update'
            : 'Cheque Deposit Add') + ' | Awecount',
      }
    })
    formData.fields.value.cheque_date =
      formData.fields.value.cheque_date || formData.today

    formData.fields.value.date = formData.fields.value.date || formData.today

    const onSubmitClick = async (status) => {
      const originalStatus = formData.fields.value.status
      formData.fields.value.status = status
      try {await formData.submitForm() } catch (err) {
        formData.fields.value.status = originalStatus
      }
    }
    return {
      ...formData,
      CreateAccount,
      BenefactorForm,
      checkPermissions,
      onSubmitClick
    }
  },
}
</script>
