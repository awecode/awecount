<template>
  <!-- <h1 class="text-h5 q-ma-lg text-bold"></h1> -->
  <q-form @submit.prevent="submitForm" class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Account</span>
          <span v-else>Update Account | {{ fields.short_name }}</span>
        </div>
      </q-card-section>

      <q-card class="q-mt-md q-ml-lg q-mr-lg q-mb-xs q-pt-md">
        <div class="q-px-sm">
          <div class="q-gutter-sm text-grey-8">
            <q-radio v-model="fields.is_wallet" :val="false" label="Bank Account, e.g. Standard Chartered" />
            <q-radio v-model="fields.is_wallet" :val="true" label="Wallet Account, e.g. eSewa, Paypal" />
          </div>
        </div>
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.account_name" label="Account Name" class="col-6" :error-message="errors.account_name"
              :error="!!errors.account_name" />
            <q-input v-if="!fields.is_wallet" v-model="fields.account_number" label="Account Number *" class="col-6"
              :error-message="errors.account_number" :error="!!errors.account_number" />
          </div>
          <div class="row q-col-gutter-md q-mt-xs">
            <q-input v-model="fields.bank_name" :label="fields.is_wallet ? 'Wallet Name, e.g. Paypal' : 'Bank Name'
              " class="col-6" :error-message="errors.bank_name" :error="!!errors.bank_name" />
            <q-input v-model="fields.short_name" label="Short Name" class="col-3" :error-message="errors.short_name"
              :error="!!errors.short_name" />
            <q-input v-if="!fields.is_wallet" v-model="fields.branch_name" label="Bank Branch" class="col-3"
              :error-message="errors.branch_name" :error="!!errors.branch_name" />
          </div>
          <div class="row col-6 q-col-gutter-md q-mt-xs">
            <q-input v-if="!fields.is_wallet" v-model="fields.next_cheque_no" label="Next Cheque No *" class="col-6"
              :error-message="errors.next_cheque_no" :error="!!errors.next_cheque_no" />
            <q-input v-else v-model.number="fields.transaction_commission_percent" label="Transaction Commission %"
              class="col-6" :error-message="errors.transaction_commission_percent"
              :error="!!errors.transaction_commission_percent" />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn v-if="checkPermissions('BankAccountCreate') && !isEdit" color="green" label="Create" class="q-ml-auto" :loading="loading"
            @click.prevent="submitForm" type="submit"/>
          <q-btn v-if="checkPermissions('BankAccountModify') && isEdit" color="green" label="Update" class="q-ml-auto" :loading="loading"
            @click.prevent="submitForm" type="submit"/>
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/bank-account/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/bank-accounts/list/',
    })
    formData.fields.value.is_wallet = false
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value
            ? 'Update Bank Account'
            : 'Add Bank Account') + ' | Awecount',
      }
    })
    watch(formData.fields.value, (newVal) => {
      if (newVal.is_wallet == true) {
        formData.fields.value.account_number = null
        formData.fields.value.next_cheque_no = null
        formData.fields.value.branch_name = null
      } else {
        formData.fields.value.transaction_commission_percent = null
      }
    })
    return {
      ...formData,
      checkPermissions
    }
  },
}
</script>
