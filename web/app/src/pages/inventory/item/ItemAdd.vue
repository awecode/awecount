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
          <div class="row q-col-gutter-md">
            <q-input class="col-6" v-model="fields.name" label="Name *" :error-message="errors.name"
              :error="!!errors.name" />
            <q-input v-model="fields.code" label="Code *" class="col-6" :error-message="errors.code"
              :error="!!errors.code" type="number" />
          </div>
          <div class="row q-col-gutter-md">
            <q-input class="col-6" v-model="fields.cost_price" label="Cost Price" type="number"
              :error-message="errors.cost_price" :error="!!errors.cost_pcoderice" />
            <q-input v-model="fields.selling_price" label="Selling Price" class="col-6"
              :error-message="errors.selling_price" :error="!!errors.selling_price" type="number" />
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <n-auto-complete class="col-6 q-full-width" label="Brand" v-model="fields.brand"
                :options="formDefaults.collections?.brands" :modal-component="BrandForm" :error="errors.brand" />
            </div>
          </div>
          <div>
            <q-input v-model="fields.description" label="Description" class="col-6" :error-message="errors.description"
              :error="!!errors.description" type="textarea" />
          </div>
          <q-card class="q-pa-lg">
            <div class="row q-col-gutter-md">
              <div class="col-6">
                <n-auto-complete class="col-6 q-full-width" label="Category" v-model="fields.category"
                  :options="formDefaults.collections?.inventory_categories" :modal-component="InventoryCategoryForm"
                  :error="errors.category" />
              </div>
            </div>
            <!-- TODO: What is Extra field, hasPerm? ? -->
            <div class="row q-col-gutter-md">
              <div class="col-6">
                <n-auto-complete class="q-full-width" label="Unit" v-model="fields.unit_id"
                  :options="formDefaults.collections?.units" :modal-component="BrandForm" :error="errors.unit_id" />
              </div>
              <!-- {{ fields.unit_id }}--uit id -->
              <div class="col-6">
                <n-auto-complete class="q-full-width" label="Tax Scheme" v-model="fields.tax_scheme_id"
                  :options="formDefaults.collections?.tax_scheme" :modal-component="TaxForm"
                  :error="errors.tax_scheme_id" />
              </div>
            </div>
            <div class="row q-col-gutter-md">
              <div class="col-6">
                <n-auto-complete class="col-6 q-full-width" label="Sales Account" v-model="fields.sales_account"
                  :options="formDefaults.collections?.accounts" :modal-component="AccountForm"
                  :error="errors.sales_account" />
              </div>
              <div class="col-6">
                <n-auto-complete class="col-6 q-full-width" label="Purchase Account" v-model="fields.purchase_account"
                  :options="formDefaults.collections?.accounts" :modal-component="AccountForm"
                  :error="errors.purchase_account" />
              </div>
            </div>
            <div class="row q-col-gutter-md">
              <div class="col-6">
                <n-auto-complete class="col-6 q-full-width" label="Discount Allowed Account"
                  v-model="fields.discount_allowed_account" :options="formDefaults.collections?.accounts"
                  :modal-component="AccountForm" :error="errors.discount_allowed_account" />
              </div>
              <div class="col-6">
                <n-auto-complete class="col-6 q-full-width" label="Discount Received Account"
                  v-model="fields.discount_received_account" :options="formDefaults.collections?.accounts"
                  :modal-component="AccountForm" :error="errors.discount_received_account" />
              </div>
            </div>
            <div class="row q-gutter-y-lg q-mt-lg">
              <q-checkbox class="col-4" v-model="fields.track_inventory" label="Track Inventory"
                :error-message="errors.track_inventory" :error="!!errors.track_inventory" />
              <q-checkbox class="col-4" v-model="fields.can_be_sold" label="Can be sold?"
                :error-message="errors.can_be_sold" :error="!!errors.can_be_sold"
                :disable="fields.direct_expense || fields.indirect_expense" />
              <q-checkbox class="col-4" v-model="fields.can_be_purchased" label="Can be purchased?"
                :error-message="errors.can_be_purchased" :error="!!errors.can_be_purchased"
                :disable="fields.direct_expense || fields.indirect_expense" />
              <q-checkbox class="col-4" v-model="fields.fixed_asset" label="Fixed Assets"
                :error-message="errors.fixed_asset" :error="!!errors.fixed_asset"
                :disable="fields.direct_expense || fields.indirect_expense" />
              <q-checkbox class="col-4" v-model="fields.direct_expense" label="Direct Expenses"
                :error-message="errors.direct_expense" :error="!!errors.direct_expense"
                @click="toggleExpenses('indirect_expense')" />
              <q-checkbox class="col-4" v-model="fields.indirect_expense" label="Indirect Expense?"
                :error-message="errors.indirect_expense" :error="!!errors.indirect_expense"
                @click="toggleExpenses('direct_expense')" />
            </div>
          </q-card>
          <div class="row justify-between q-pa-sm q-mt-md">
            <div class="col-5 row q-col-gutter-md items-end" v-if="
              typeof fields.front_image === 'string' && fields.front_image
            ">
              <div>Front Image</div>
              <div>
                <q-btn target="_blank" class="info" color="blue" :href="fields.front_image">PREVIEW</q-btn>
              </div>
              <div>
                <q-btn color="orange-7" class="ml-5" style="cursor: pointer" @click="clear('front_image')">clear</q-btn>
              </div>
            </div>
            <div v-else class="col-5">
              <q-file v-model="images.front_image" class="col-5 q-full-width" :error-messages="errors.front_image"
                label="Front Image" @update:model-value="
                  onFileChange(fields, $event, 'front_image')
                ">
                <template v-slot:prepend>
                  <q-icon name="attach_file" />
                </template>
              </q-file>
            </div>
            <div class="col-5 row q-col-gutter-md items-end"
              v-if="typeof fields.back_image === 'string' && fields.back_image">
              <div>Back Image</div>
              <div>
                <q-btn target="_blank" class="info" color="blue" :href="fields.back_image">PREVIEW</q-btn>
              </div>
              <div>
                <q-btn color="orange-7" class="ml-5" style="cursor: pointer" @click="clear('back_image')">clear</q-btn>
              </div>
            </div>
            <div v-else class="col-5">
              <q-file v-model="fields.back_image" class="col-5 q-full-width" :error-messages="errors.back_image"
                label="Back Image" @update:model-value="onFileChange(fields, $event, 'back_image')">
                <template v-slot:prepend>
                  <q-icon name="attach_file" />
                </template>
              </q-file>
            </div>
            <!-- <div
              class="col-5"
              v-if="typeof fields.back_image === 'string' && fields.back_image"
            >
              <div class="row">
                <div>Front Image agshah</div>
                <q-btn target="_blank" class="info" :href="fields.back_image"
                  >PREVIEW</q-btn
                >
                <span
                  class="btn btn-info btn-fill ml-5"
                  style="cursor: pointer"
                  @click="clear('back_image')"
                  >clear</span
                >
              </div>
            </div>
            <div v-else class="col-5">
              <q-file
                v-model="images.back_image"
                class="col-5 q-full-width"
                :error-messages="errors.back_image"
                label="Back Image"
                @update:model-value="onFileChange(fields, $event, 'back_image')"
              >
                <template v-slot:prepend>
                  <q-icon name="attach_file" />
                </template>
              </q-file>
            </div> -->
          </div>

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
        <div class="q-mt-lg text-right q-pr-md q-pb-lg">
          <q-btn @click.prevent="submitForm" color="primary" :label="isEdit ? 'Update' : 'Create'"
            class="q-ml-auto q-px-xl" />
        </div>
      </q-card>
    </q-card>
    <!-- <v-row>
      <v-col cols="12" sm="6">
        <v-row
          v-if="typeof fields.back_image === 'string' && fields.back_image"
        >
          <v-subheader>Back Image</v-subheader>
          <v-btn target="_blank" class="info" :href="fields.back_image"
            >PREVIEW</v-btn
          >
          <span
            class="btn btn-info btn-fill ml-5"
            style="cursor: pointer"
            @click="clear(fields, 'back_image')"
            >clear</span
          >
        </v-row>
        <v-file-input
          v-else
          label="Back Image"
          :error-messages="form.errors.get('back_image')"
          @change="onFileChange(fields, $event, 'back_image')"
        ></v-file-input>
      </v-col>
    </v-row> -->
  </q-form>
</template>

<script setup>
import NAutoComplete from 'src/components/NAutoComplete.vue'
import BrandForm from 'src/pages/inventory/product/brand/BrandForm.vue'
import InventoryCategoryForm from 'src/pages/inventory/product/category/InventoryCategoryForm.vue'
import TaxForm from 'src/pages/tax/scheme/TaxForm.vue'
import AccountForm from 'src/pages/bank/account/AccountForm.vue'
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
const toggleExpenses = (type) => {
  fields.value[type] = false
}
const images = ref({
  front_image: null,
  back_image: null,
})
const endpoint = '/v1/items/'
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
  successRoute: '/items/list/',
})

const isExpenses = computed(
  () => fields.value.direct_expense || fields.value.indirect_expense
)

watch(isExpenses, () => {
  if (isExpenses.value === true) {
    fields.value.track_inventory = false
    fields.value.can_be_sold = false
    fields.value.fixed_asset = false
    fields.value.can_be_purchased = false
  }
})
const onFileChange = (dct, event, attr) => {
  const file = event
  let reader = new FileReader()
  reader.readAsDataURL(file)
  reader.fileName = file.name
  reader.onload = () => {
    fields.value[`${attr}`] = {
      name: reader.fileName,
      data: reader.result,
    }
  }
  reader.onerror = function (error) {
    console.error('Error: ', error)
  }
}
const clear = (field) => (fields.value[field] = null)
// onMounted(() => {
//   fields.value.direct_expense = false;
//   fields.value.indirect_expense = false;
//   fields.value.track_inventory = false;
//   fields.value.can_be_sold = false;
//   fields.value.fixed_asset = false;
//   fields.value.can_be_purchased = false;
// });
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
