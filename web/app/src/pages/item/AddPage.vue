<template>
  <div class="q-pa-md text-grey-8 bg-grey-4">
    <h4 class="q-ma-none text-weight-bold q-mb-md">New Item</h4>
    <q-form @submit.prevent="submitForm" class="bg-white q-pa-md q-pb-xl column q-gutter-sm">
      <div class="twoInputField">
        <div>
          <q-input v-model="fields.name" label="Name" :error="errors?.party" />
        </div>
        <div>
          <q-input v-model="fields.code" label="Code" />
        </div>
      </div>
      <div class="twoInputField">
        <div>
          <q-input v-model="fields.cost_price" type="number" label="Cost Price" />
        </div>
        <div>
          <q-input v-model="fields.selling_price" type="number" label="Selling Price" />
        </div>
      </div>
      <div class="twoInputField">
        <div>
          <q-select v-model="fields.brand" :options="formDefaults.collections?.brands" label="Brands" />
        </div>
      </div>
      <q-btn @click.prevent="submitForm" color="primary" label="Submit" class="q-ml-auto" />
    </q-form>
    <!-- {{ formDefaults }}--formDefaults -->
  </div>
</template>

<script>
// import LedgerForm from '../account/ledger/LedgerForm.vue'
import useForm from '/src/composables/useForm'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/items/'
    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/items/',
      }),
      // LedgerForm,
    }
  },
}
// const endpoint = '/v1/items/'
// console.log(useForm(endpoint, {
//   getDefaults: true,
//   successRoute: '/income/item/',
// }))
</script>

<style scoped>
.twoInputField {
  display: grid;
  grid-template-columns: auto auto;
  column-gap: 15px;
}

@media (max-width: 600px) {
  .twoInputField {
    grid-template-columns: auto;
    column-gap: 15px;
    row-gap: 15px;
  }
}
</style>
