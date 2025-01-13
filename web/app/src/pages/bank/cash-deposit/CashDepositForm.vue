<script>
import checkPermissions from 'src/composables/checkPermissions'
import BenefactorForm from 'src/pages/account/ledger/LedgerForm.vue'
import CreateAccount from '../account/AccountForm.vue'
import useForm from '/src/composables/useForm'

export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/bank-cash-deposits/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/cash-deposit/list/',
    })
    const isDeleteOpen = ref(false)
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Cash Deposit Update' : 'Cash Deposit Add'} | Awecount`,
      }
    })
    formData.fields.value.date = formData.fields.value.date || formData.today

    return {
      ...formData,
      CreateAccount,
      BenefactorForm,
      checkPermissions,
      isDeleteOpen,
    }
  },
}
</script>

<template>
  <q-form autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Cash Deposit</span>
          <span v-else>Update Cash Deposit</span>
        </div>
      </q-card-section>
      <q-card class="q-ma-sm q-pt-md">
        <q-card class="q-pa-lg">
          <div class="row q-col-gutter-md">
            <div class="col-md-6 col-12">
              <n-auto-complete-v2
                v-model="fields.bank_account"
                endpoint="v1/bank-cash-deposits/create-defaults/bank_accounts"
                label="Bank Account *"
                :error="errors?.bank_account"
                :modal-component="checkPermissions('BankAccountCreate') ? CreateAccount : null"
                :options="formDefaults.collections?.bank_accounts"
                :static-option="fields.selected_bank_account_obj"
              />
            </div>
            <div class="col-md-6 col-12">
              <n-auto-complete-v2
                v-model="fields.benefactor"
                endpoint="v1/bank-cash-deposits/create-defaults/benefactors"
                label="Benefactor *"
                :error="errors?.benefactor"
                :modal-component="checkPermissions('AccountCreate') ? BenefactorForm : null"
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
              label="Deposit Date *"
              :error="!!errors.date"
              :error-message="errors.date"
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
          <div class="row">
            <q-input
              v-model="fields.narration"
              autogrow
              class="col-12 q-mt-md"
              label="Narration"
              type="textarea"
              :error="!!errors.narration"
              :error-message="errors.narration"
            />
          </div>
        </q-card>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn
            v-if="checkPermissions('BankCashDepositCreate') && !isEdit"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('BankCashDepositModify') && isEdit"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="fields?.status == 'Cleared' && checkPermissions('BankCashDepositCancel')"
            color="red"
            icon="block"
            label="Cancel"
            :loading="loading"
            @click.prevent="isDeleteOpen = true"
          />
          <q-btn
            v-if="fields?.status && fields?.status != 'Cancelled' && checkPermissions('BankCashDepositModify')"
            class="text-h7 q-py-sm"
            color="blue"
            icon="library_books"
            label="Journal Entries"
            :loading="loading"
            :to="`/journal-entries/bank-cash-deposits/${id}/`"
          />
        </div>
      </q-card>
    </q-card>
    <q-dialog v-model="isDeleteOpen">
      <q-card style="min-width: min(40vw, 400px)">
        <q-card-section class="bg-red-6 q-py-md flex justify-between">
          <div class="text-h6 text-white">
            <span>Confirm Cancellation?</span>
          </div>
          <q-btn
            v-close-popup
            dense
            flat
            round
            class="text-red-700 bg-slate-200 opacity-95"
            icon="close"
          />
        </q-card-section>
        <q-separator inset />
        <q-card-section>
          <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500">
            Are you sure?
          </div>
          <div class="text-blue">
            <div class="row justify-end">
              <q-btn
                flat
                class="q-mr-md text-blue-grey-9"
                label="NO"
                @click="() => (isDeleteOpen = false)"
              />
              <q-btn
                flat
                class="text-red"
                label="Yes"
                @click="cancelForm"
              />
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-form>
</template>
