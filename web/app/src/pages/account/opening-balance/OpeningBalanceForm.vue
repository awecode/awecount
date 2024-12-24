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
      successRoute: '/account-opening-balance/',
    })
    useMeta(() => {
      return {
        title:
          `${formData.isEdit?.value
            ? 'Update Account Opening Balances'
            : 'Add Account Opening Balances'} | Awecount`,
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
          <div class="grid md:grid-cols-2 q-col-gutter-md">
            <div>
              <n-auto-complete-v2
                v-if="!isEdit"
                v-model="fields.account"
                :endpoint="`/api/company/${$route.params.company}/account-opening-balance/create-defaults/accounts`"
                :static-option="fields.selected_account_obj"
                :options="formDefaults.collections?.accounts"
                label="Account *"
                :modal-component="checkPermissions('account.create') ? LedgerForm : null"
                :error="errors?.account"
              />
              <q-input v-else label="Account *" disable :model-value="fields.name" class="mb-4" />
            </div>
          </div>
          <div class="grid md:grid-cols-2 q-col-gutter-md">
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
            v-if="checkPermissions('accountopeningbalance.create') && !isEdit"
            color="green"
            label="Create"
            class="q-ml-auto"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('accountopeningbalance.modify') && isEdit"
            color="green"
            label="Update"
            class="q-ml-auto"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>
