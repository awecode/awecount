<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Opening Balance</span>
          <span v-else>Update Opening Balance</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-mb-lg">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-12">
              <n-auto-complete
                v-model="fields.account"
                :options="formDefaults.collections?.accounts"
                label="Account"
                :modal-component="LedgerForm"
                :error="errors?.account"
              />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.opening_dr"
              type="number"
              label="Opening Dr"
              class="col-6"
              :error-message="errors.opening_dr"
              :error="!!errors.opening_dr"
            />
            <q-input
              v-model="fields.opening_cr"
              type="number"
              label="Opening Cr"
              class="col-6"
              :error-message="errors.opening_cr || errors.detail"
              :error="!!errors.opening_cr || !!errors.detail"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            @click.prevent="submitForm"
            color="primary"
            :label="isEdit ? 'Update' : 'Create'"
            class="q-ml-auto"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import LedgerForm from '/src/pages/account/ledger/LedgerForm.vue'

export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/account-opening-balance/'
    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/account/opening-balance/',
      }),
      LedgerForm,
    }
  },
}
</script>
