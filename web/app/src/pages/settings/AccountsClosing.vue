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
                            <q-icon name="mdi-exclamation" size="sm"></q-icon> Please Choose the Financial year you want to
                            close.
                        </div>
                        <div class="q-my-md row">
                            <q-select v-model="fields.fiscal_year" class="col-12 col-sm-6" label="Financial Year"
                                :options="formDefaults.collections?.fiscal_years" option-value="id" option-label="name"
                                map-options emit-value></q-select>
                        </div>
                        <q-btn v-if="checkPermissions('AccountClosingCreate')" class="q-mt-md" color="green" type="submit" :loading="loading">
                            Close Accounts
                        </q-btn>
                    </div>
                </div>
            </q-card-section>
        </q-form>
    </q-card>
</template>

<script setup>
const $q = useQuasar()
import checkPermissions from 'src/composables/checkPermissions'
// const fiscal_year = ref(null)
const endpoint = '/v1/account-closing/'
const { fields, errors, isEdit, formDefaults, submitForm, loading } = useForm(endpoint, {
    getDefaults: true,
    successRoute: '/settings/account-closing/'
    
})
watch(() => formDefaults.value, (newVal) => {
    if (newVal.fields.current_fiscal_year_id) {
        fields.value.fiscal_year = newVal.fields.current_fiscal_year_id
    }
})
</script>