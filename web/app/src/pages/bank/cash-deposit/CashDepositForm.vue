<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'
import BenefactorForm from 'src/pages/account/ledger/LedgerForm.vue'
import CreateAccount from '../account/AccountForm.vue'

export default {
  setup() {
    const endpoint = `/api/company/${route.params.company}/bank-cash-deposits/`
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/cash-deposit/list/',
    })
    const isDeleteOpen = ref(false)
    useMeta(() => {
      return {
        title:
          `${formData.isEdit?.value
            ? 'Cash Deposit Update'
            : 'Cash Deposit Add'} | Awecount`,
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
  <q-form class="q-pa-lg" autofocus>
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
                :options="formDefaults.collections?.bank_accounts"
                :endpoint="`/api/company/${$route.params.company}/bank-cash-deposits/create-defaults/bank_accounts`"
                :static-option="fields.selected_bank_account_obj"
                label="Bank Account *"
                :modal-component="checkPermissions('bankaccount.create') ? CreateAccount : null"
                :error="errors?.bank_account"
              />
            </div>
            <div class="col-md-6 col-12">
              <n-auto-complete-v2
                v-model="fields.benefactor"
                :options="formDefaults.collections?.benefactors"
                :endpoint="`/api/company/${$route.params.company}/bank-cash-deposits/create-defaults/benefactors`"
                :static-option="fields.selected_benefactor_obj"
                label="Benefactor *"
                :modal-component="checkPermissions('account.create') ? BenefactorForm : null"
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
              type="number"
            />
            <date-picker
              v-model="fields.date"
              class="col-md-6 col-12"
              label="Deposit Date *"
              :error-message="errors.date"
              :error="!!errors.date"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.voucher_no"
              label="Voucher Number"
              class="col-md-6 col-12"
              :error-message="errors.voucher_no"
              :error="!!errors.voucher_no"
              type="number"
            />
            <q-input
              v-model="fields.deposited_by"
              label="Deposited By"
              class="col-md-6 col-12"
              :error-message="errors.deposited_by"
              :error="!!errors.deposited_by"
            />
          </div>
          <div class="row">
            <q-input
              v-model="fields.narration"
              label="Narration"
              class="col-12 q-mt-md"
              type="textarea"
              autogrow
              :error-message="errors.narration"
              :error="!!errors.narration"
            />
          </div>
        </q-card>
        <div class="text-right q-pr-md q-pb-lg flex gap-4 justify-end">
          <q-btn
            v-if="checkPermissions('bankcashdeposit.create') && !isEdit"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('bankcashdeposit.modify') && isEdit"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="fields?.status == 'Cleared' && checkPermissions('bankcashdeposit.cancel')"
            icon="block"
            color="red"
            label="Cancel"
            :loading="loading"
            @click.prevent="isDeleteOpen = true"
          />
          <q-btn
            v-if="fields?.status && fields?.status != 'Cancelled' && checkPermissions('bankcashdeposit.modify')"
            :to="`/${$route.params.company}/journal-entries/bank-cash-deposits/${id}/`"
            color="blue"
            icon="library_books"
            label="Journal Entries"
            class="text-h7 q-py-sm"
            :loading="loading"
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
          <q-btn v-close-popup icon="close" class="text-red-700 bg-slate-200 opacity-95" flat round dense />
        </q-card-section>
        <q-separator inset />
        <q-card-section>
          <div class="q-mb-md text-grey-9" style="font-size: 16px; font-weight: 500;">
            Are you sure?
          </div>
          <div class=" text-blue">
            <div class="row justify-end">
              <q-btn flat class="q-mr-md text-blue-grey-9" label="NO" @click="() => (isDeleteOpen = false)" />
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
