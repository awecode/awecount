<script>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'
import LedgerForm from 'src/pages/account/ledger/LedgerForm.vue'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/account-opening-balance/`
    const formData = useForm(endpoint, {
      getDefaults: true,
      successRoute: `/${route.params.company}/account/opening-balances/`,
    })
    useMeta(() => {
      return {
        title: `${formData.isEdit?.value ? 'Update Account Opening Balances' : 'Add Account Opening Balances'} | Awecount`,
      }
    })
    return {
      ...formData,
      LedgerForm,
      checkPermissions,
    }
  },
}
</script>

<template>
  <q-form autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Opening Balance</span>
          <span v-else>Update Opening Balance</span>
        </div>
      </q-card-section>

      <q-card class="q-mx-lg q-mb-lg">
        <q-card-section>
          <div class="grid md:grid-cols-2 q-col-gutter-md">
            <div>
              <n-auto-complete-v2
                v-if="!isEdit"
                v-model="fields.account"
                label="Account *"
                :endpoint="`/api/company/${$route.params.company}/account-opening-balance/create-defaults/accounts`"
                :error="errors?.account"
                :modal-component="checkPermissions('account.create') ? LedgerForm : null"
                :options="formDefaults.collections?.accounts"
                :static-option="fields.selected_account_obj"
              />
              <q-input
                v-else
                disable
                class="mb-4"
                label="Account *"
                :model-value="fields.name"
              />
            </div>
          </div>
          <div class="grid md:grid-cols-2 q-col-gutter-md">
            <q-input
              v-model="fields.opening_dr"
              class="col-6"
              label="Opening Dr"
              type="number"
              :error="!!errors.opening_dr"
              :error-message="errors.opening_dr"
            />
            <q-input
              v-model="fields.opening_cr"
              class="col-6"
              label="Opening Cr"
              type="number"
              :error="!!errors.opening_cr || !!errors.detail"
              :error-message="errors.opening_cr || errors.detail"
            />
          </div>
        </q-card-section>
        <div class="text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('accountopeningbalance.create') && !isEdit"
            class="q-ml-auto"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('accountopeningbalance.modify') && isEdit"
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
