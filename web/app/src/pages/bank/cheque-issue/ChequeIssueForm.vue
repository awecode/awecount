<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Cheque Issue</span>
          <span v-else>Update Cheque Issue</span>
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
                :disabled="isEdit"
                :error="errors?.bank_account"
              />
            </div>
            <date-picker
              v-model="fields.date"
              class="col-md-6 col-12"
              label="Date *"
              :error-message="errors.date"
              :error="!!errors.date"
            ></date-picker>
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.cheque_no"
              label="Cheque Number"
              class="col-md-6 col-12"
              :error-message="errors.cheque_no"
              :error="!!errors.cheque_no"
              :disable="isEdit"
            />
            <q-input
              v-model="fields.amount"
              label="Amount *"
              class="col-md-6 col-12"
              :error-message="errors.amount"
              :error="!!errors.amount"
            />
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-8">
              <n-auto-complete
                v-if="!showDrAccount"
                v-model="fields.party"
                :options="formDefaults.collections?.parties"
                label="Party *"
                :error="errors?.party"
              />
              <div class="row" v-else>
                <q-input
                  v-model="fields.issued_to"
                  label="Issued To"
                  class="col-12"
                  :error-message="errors.issued_to"
                  :error="!!errors.issued_to"
                />
              </div>
            </div>
            <div>
              <q-btn
                @click.prevent="toggleDrAccount"
                square
                icon="groups_2"
                class="q-mt-md"
              />
            </div>
          </div>
          <div class="row q-col-gutter-md" v-if="showDrAccount">
            <div class="col-8">
              <n-auto-complete
                v-model="fields.dr_account"
                :options="formDefaults.collections?.accounts"
                label="Dr Account"
                :modal-component="BenefactorForm"
                :error="errors?.dr_account"
              />
            </div>
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            @click.prevent="submitForm"
            color="primary"
            :label="isEdit ? 'Update' : 'Create'"
            class="q-ml-auto"
          />
          <q-btn
            v-if="fields?.status == 'Issued'"
            @click.prevent="cancelForm"
            icon="block"
            color="red"
            :label="'Cancel'"
            class="q-ml-md"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import BenefactorForm from '/src/components/BenefactorForm.vue'
// const $q = useQuasar()

export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/cheque-issue/'
    const showDrAccount = ref(false)
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/bank/cheque-issue/',
    })

    formData.fields.value.date = formData.fields.value.date || formData.today

    const toggleDrAccount = () => {
      showDrAccount.value = !showDrAccount.value
      formData.fields.value.issued_to = null
      formData.fields.value.dr_account = null
      formData.fields.value.party = null
    }
    console.log(formData.fields.value.issued_to)

    if (formData.fields.value.issued_to || formData.fields.value.dr_account) {
      showDrAccount.value = true
    }

    watch(formData.fields, (a) => {
      if (a.issued_to || a.dr_account) {
        showDrAccount.value = true
      }
    })

    return {
      ...formData,
      showDrAccount,
      BenefactorForm,
      toggleDrAccount,
    }
  },
}
</script>
