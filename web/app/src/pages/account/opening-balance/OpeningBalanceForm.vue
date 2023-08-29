<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Opening Balance</span>
          <span v-else>Update Opening Balance</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-mb-lg">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <n-auto-complete v-model="fields.account" :options="formDefaults.collections?.accounts" label="Account"
                :modal-component="checkPermissions('AccountCreate') ? LedgerForm : null" :error="errors?.account" />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <q-input v-model="fields.opening_dr" type="number" label="Opening Dr" class="col-6"
              :error-message="errors.opening_dr" :error="!!errors.opening_dr" />
            <q-input v-model="fields.opening_cr" type="number" label="Opening Cr" class="col-6"
              :error-message="errors.opening_cr || errors.detail" :error="!!errors.opening_cr || !!errors.detail" />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn v-if="checkPermissions('AccountOpeningBalanceCreate') && !isEdit" @click.prevent="submitForm"
            color="green" label="Create" class="q-ml-auto" type="submit" />
          <q-btn v-if="checkPermissions('AccountOpeningBalanceModify') && isEdit" @click.prevent="submitForm"
            color="green" label="Update" class="q-ml-auto" type="submit" />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script>
import useForm from '/src/composables/useForm'
import LedgerForm from '/src/pages/account/ledger/LedgerForm.vue'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/account-opening-balance/'
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: '/account-opening-balance/',
    })
    useMeta(() => {
      return {
        title:
          (formData.isEdit?.value
            ? 'Update Account Opening Balances'
            : 'Add Account Opening Balances') + ' | Awecount',
      }
    })
    return {
      ...formData,
      LedgerForm,
      checkPermissions
    }
  },
}
</script>
