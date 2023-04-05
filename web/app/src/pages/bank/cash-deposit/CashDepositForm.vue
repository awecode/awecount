<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Cash Deposit</span>
          <span v-else>Update Cash Deposit</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-ma-sm q-pt-md">
        <q-card-section>
          <q-card class="q-pa-lg">
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
                label="Deposit Date *"
                :error-message="errors.date"
                :error="!!errors.date"
              ></date-picker>
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
          </q-card>
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
        </q-card-section>

        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            @click.prevent="submitForm"
            color="green"
            :label="isEdit ? 'Update' : 'Create'"
            class="q-ml-auto"
          />
          <q-btn
            v-if="fields?.status == 'Cleared'"
            @click.prevent="cancelForm"
            icon="block"
            color="red"
            :label="'Cancel'"
            class="q-ml-md"
          />
          <q-btn
            v-if="fields?.status && fields?.status != 'Cancelled'"
            :to="`/journal-entries/bank-cash-deposits/${id}/`"
            color="blue"
            icon="library_books"
            label="Journal Entries"
            class="text-h7 q-py-sm q-ml-md"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import CreateAccount from '../account/AccountForm.vue'
import useForm from '/src/composables/useForm'
import BenefactorForm from '/src/components/BenefactorForm.vue'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/bank-cash-deposits/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/cash-deposit/list/',
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value
            ? 'Cash Deposit Update'
            : 'Cash Deposit Add') + ' | Awecount',
      }
    })
    formData.fields.value.date = formData.fields.value.date || formData.today

    return {
      ...formData,
      CreateAccount,
      BenefactorForm,
    }
  },
}
</script>
