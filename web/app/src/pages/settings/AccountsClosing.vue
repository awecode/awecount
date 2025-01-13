<script setup>
import checkPermissions from 'src/composables/checkPermissions'
// const fiscal_year = ref(null)
const route = useRoute()
const endpoint = `/api/company/${route.params.company}/account-closing/`
const metaData = {
  title: 'Account Closing | Awecount',
}
useMeta(metaData)
const { fields, formDefaults, submitForm, loading } = useForm(endpoint, {
  getDefaults: true,
  successRoute: '/settings/account-closing/',
})
watch(
  () => formDefaults.value,
  (newVal) => {
    if (newVal.fields.current_fiscal_year?.id) {
      fields.value.fiscal_year = newVal.fields.current_fiscal_year.id
    }
  },
)
</script>

<template>
  <q-card class="q-ma-lg">
    <q-form autofocus @submit="submitForm">
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Accounts Closing</span>
        </div>
      </q-card-section>
      <q-card-section>
        <div class="text-grey-9">
          <div>
            <div class="text-weight-medium text-grey-7">
              <q-icon name="mdi-exclamation" size="sm" />
              Please Choose the Financial year you want to close.
            </div>
            <div class="q-my-md row">
              <div class="col-12 col-sm-6">
                <n-auto-complete-v2 v-model="fields.fiscal_year" label="Financial Year" :endpoint="`/api/company/${$route.params.company}/account-closing/create-defaults/fiscal_years`" :static-option="formDefaults?.fields?.current_fiscal_year" :options="formDefaults.collections?.fiscal_years" option-value="id" option-label="name" map-options emit-value />
              </div>
            </div>
            <q-btn v-if="checkPermissions('accountclosing.create')" class="q-mt-md" color="green" type="submit" :loading="loading">Close Accounts</q-btn>
          </div>
        </div>
      </q-card-section>
    </q-form>
  </q-card>
</template>
