<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/bank-account/`
    const formData = useForm(endpoint, {
      getDefaults: false,
      successRoute: '/bank-accounts/list/',
    })
    formData.fields.value.is_wallet = false
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Update Bank Account' : 'Add Bank Account'} | Awecount`,
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
      checkPermissions,
    }
  },
}
</script>

<template>
  <!-- <h1 class="text-h5 q-ma-lg text-bold"></h1> -->
  <q-form class="q-pa-lg" @submit.prevent="submitForm">
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
            <q-radio v-model="fields.is_wallet" label="Bank Account, e.g. Standard Chartered" :val="false" />
            <q-radio v-model="fields.is_wallet" label="Wallet Account, e.g. eSewa, Paypal" :val="true" />
          </div>
        </div>
        <q-card-section>
          <div class="q-col-gutter-md grid lg:grid-cols-2">
            <q-input
              v-model="fields.account_name"
              class="col-6"
              label="Account Name"
              :error="!!errors.account_name"
              :error-message="errors.account_name"
            />
            <q-input
              v-if="!fields.is_wallet"
              v-model="fields.account_number"
              class="col-6"
              label="Account Number *"
              :error="!!errors.account_number"
              :error-message="errors.account_number"
            />
          </div>
          <div class="q-col-gutter-md grid lg:grid-cols-2">
            <q-input
              v-model="fields.bank_name"
              class="col-6"
              :error="!!errors.bank_name"
              :error-message="errors.bank_name"
              :label="fields.is_wallet ? 'Wallet Name, e.g. Paypal' : 'Bank Name'"
            />
            <div class="grid sm:grid-cols-2 q-col-gutter-md">
              <q-input
                v-model="fields.short_name"
                class="col-3"
                label="Short Name"
                :error="!!errors.short_name"
                :error-message="errors.short_name"
              />
              <q-input
                v-if="!fields.is_wallet"
                v-model="fields.branch_name"
                class="col-3"
                label="Bank Branch"
                :error="!!errors.branch_name"
                :error-message="errors.branch_name"
              />
            </div>
          </div>
          <div class="grid sm:grid-cols-2 q-col-gutter-md q-mt-xs">
            <q-input
              v-if="!fields.is_wallet"
              v-model="fields.next_cheque_no"
              class="col-6"
              label="Next Cheque No *"
              :error="!!errors.next_cheque_no"
              :error-message="errors.next_cheque_no"
            />
            <q-input
              v-else
              v-model.number="fields.transaction_commission_percent"
              class="col-6"
              label="Transaction Commission %"
              :error="!!errors.transaction_commission_percent"
              :error-message="errors.transaction_commission_percent"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('bankaccount.create') && !isEdit"
            class="q-ml-auto"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('bankaccount.modify') && isEdit"
            class="q-ml-auto"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
