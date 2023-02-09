<template>
  <q-form class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Item</span>
          <span v-else>Update Item</span>
        </div>
      </q-card-section>
      <q-separator inset />
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <q-input
              class="col-6"
              v-model="fields.name"
              label="Name"
              :error-message="errors.name"
              :error="!!errors.party"
            />
            <q-input
              v-model="fields.code"
              label="Code"
              class="col-6"
              :error-message="errors.code"
              :error="!!errors.code"
              type="number"
            />
          </div>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <q-input
              class="col-6"
              v-model="fields.cost_price"
              label="Cost Price"
              type="number"
              :error-message="errors.cost_price"
              :error="!!errors.cost_pcoderice"
            />
            <q-input
              v-model="fields.selling_price"
              label="Selling Price"
              class="col-6"
              :error-message="errors.selling_price"
              :error="!!errors.selling_price"
              type="number"
            />
          </div>
          <div class="row q-col-gutter-md q-gutter-y-md">
            <div class="col-6">
              <n-auto-complete
                class="col-6 q-full-width"
                label="Brand"
                :modelValue="fields.brands"
                :options="formDefaults.collections?.brands"
                :modal-component="BrandForm"
                :error-message="errors.brand"
                :error="!!errors.brand"
              />
            </div>
          </div>
          <div>
            <q-input
              v-model="fields.description"
              label="Description"
              class="col-6"
              :error-message="errors.description"
              :error="!!errors.description"
              type="textarea"
            />
          </div>
          <q-card class="q-pa-lg">
            <div class="row q-col-gutter-md q-gutter-y-md">
              <div class="col-6">
                <n-auto-complete
                  class="col-6 q-full-width"
                  label="Category"
                  :modelValue="fields.category"
                  :options="formDefaults.collections?.inventory_categories"
                  :modal-component="BrandForm"
                  :error-message="errors.category"
                  :error="!!errors.category"
                />
              </div>
            </div>
            <!-- TODO: What is Extra field, hasPerm? ? -->
            <div class="row q-col-gutter-md q-gutter-y-md">
              <div class="col-6">
                <n-auto-complete
                  class="col-6 q-full-width"
                  label="Unit"
                  :modelValue="fields.unit_id"
                  :options="formDefaults.collections?.units"
                  :modal-component="BrandForm"
                  :error-message="errors.unit_id"
                  :error="!!errors.unit_id"
                />
              </div>
              <div class="col-6">
                <n-auto-complete
                  class="col-6 q-full-width"
                  label="Category"
                  :modelValue="fields.tax_scheme_id"
                  :options="formDefaults.collections?.tax_scheme"
                  :modal-component="BrandForm"
                  :error-message="errors.tax_scheme_id"
                  :error="!!errors.tax_scheme_id"
                />
              </div>
            </div>
            <div class="row q-col-gutter-md q-gutter-y-md">
              <div class="col-6">
                <n-auto-complete
                  class="col-6 q-full-width"
                  label="Sales Account"
                  :modelValue="fields.sales_account"
                  :options="formDefaults.collections?.accounts"
                  :modal-component="BrandForm"
                  :error-message="errors.sales_account"
                  :error="!!errors.sales_account"
                />
              </div>
              <div class="col-6">
                <n-auto-complete
                  class="col-6 q-full-width"
                  label="Purchase Account"
                  :modelValue="fields.purchase_account"
                  :options="formDefaults.collections?.purchase_account"
                  :modal-component="BrandForm"
                  :error-message="errors.purchase_account"
                  :error="!!errors.purchase_account"
                />
              </div>
            </div>
            <div class="row q-col-gutter-md q-gutter-y-md">
              <div class="col-6">
                <n-auto-complete
                  class="col-6 q-full-width"
                  label="Discount Allowed Account"
                  :modelValue="fields.discount_allowed_account"
                  :options="formDefaults.collections?.discount_allowed_account"
                  :modal-component="BrandForm"
                  :error-message="errors.discount_allowed_account"
                  :error="!!errors.discount_allowed_account"
                />
              </div>
              <div class="col-6">
                <n-auto-complete
                  class="col-6 q-full-width"
                  label="Discount Received Account"
                  :modelValue="fields.discount_received_account"
                  :options="formDefaults.collections?.discount_received_account"
                  :modal-component="BrandForm"
                  :error-message="errors.discount_received_account"
                  :error="!!errors.discount_received_account"
                />
              </div>
            </div>
            <div class="row q-gutter-y-lg q-mt-lg">
              <q-checkbox
                class="col-4"
                v-model="fields.track_inventory"
                label="Track Inventory"
                :error-message="errors.track_inventory"
                :error="!!errors.track_inventory"
              />
              <q-checkbox
                class="col-4"
                v-model="fields.can_be_sold"
                label="Can be sold?"
                :error-message="errors.can_be_sold"
                :error="!!errors.can_be_sold"
                :disable="fields.direct_expense || fields.indirect_expense"
              />
              <q-checkbox
                class="col-4"
                v-model="fields.can_be_purchased"
                label="Can be purchased?"
                :error-message="errors.can_be_purchased"
                :error="!!errors.can_be_purchased"
                :disable="fields.direct_expense || fields.indirect_expense"
              />
              <q-checkbox
                class="col-4"
                v-model="fields.fixed_asset"
                label="Track Inventory"
                :error-message="errors.fixed_asset"
                :error="!!errors.fixed_asset"
                :disable="fields.direct_expense || fields.indirect_expense"
              />
              <q-checkbox
                class="col-4"
                v-model="fields.direct_expense"
                label="Direct Expenses"
                :error-message="errors.direct_expense"
                :error="!!errors.direct_expense"
              />
              <q-checkbox
                class="col-4"
                v-model="fields.indirect_expense"
                label="Indirect Expense?"
                :error-message="errors.indirect_expense"
                :error="!!errors.indirect_expense"
              />
            </div>
          </q-card>
          <!-- <div>
            <q-input
              v-model="fields.selling_price"
              label="Code"
              class="col-6"
              :error-message="errors.selling_price"
              :error="!!errors.selling_price"
              type="number"
            />
          </div> -->
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
    {{ fields }}
    {{ isExpenses }}
  </q-form>
</template>

<script setup>
import NAutoComplete from 'src/components/NAutoComplete.vue';
import BrandForm from '../inventory/product/brand/BrandForm.vue';
// export default {
//   components: { NAutoComplete },
//   // eslint-disable-next-line @typescript-eslint/no-unused-vars
//   setup(props, context) {
//     const endpoint = '/v1/items/';
//     const fields = ref({
//       direct_expense: false,
//     });
//     watch(fields.direct_expense, () => console.log('Di changed'));
//     return {
//       ...useForm(endpoint, {
//         getDefaults: true,
//         successRoute: '/items/',
//       }),
//       BrandForm,
//     };
//   },
// };
const endpoint = '/v1/items/';
const {
  fields,
  errors,
  isEdit,
  id,
  formDefaults,
  isModal,
  today,
  submitForm,
  cancel,
  cancelForm,
} = useForm(endpoint, {
  getDefaults: true,
  successRoute: '/items/',
});

const isExpenses = computed(
  () => fields.value.direct_expense || fields.value.indirect_expense
);

watch(isExpenses, () => {
  if (isExpenses.value === true) {
    console.log('time to disable all btns');
    fields.value.track_inventory = false;
    fields.value.can_be_sold = false;
    fields.value.fixed_asset = false;
    fields.value.can_be_purchased = false;
  }
});
onMounted(() => {
  fields.value.direct_expense = false;
  fields.value.indirect_expense = false;
  fields.value.track_inventory = false;
  fields.value.can_be_sold = false;
  fields.value.fixed_asset = false;
  fields.value.can_be_purchased = false;
});
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
