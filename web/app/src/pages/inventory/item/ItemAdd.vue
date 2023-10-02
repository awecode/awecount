<template>
  <q-form class="q-pa-lg" autofocus>
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="!isEdit">New Item</span>
          <span v-else>Update Item</span>
        </div>
      </q-card-section>
      <q-card class="q-mx-lg q-pt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <q-input class="col-12 col-md-6" v-model="fields.name" label="Name *" :error-message="errors.name"
              :error="!!errors.name" />
            <q-input v-model="fields.code" label="Code *" class="col-12 col-md-6" :error-message="errors.code"
              :error="!!errors.code" />
          </div>
          <div class="row q-col-gutter-md">
            <q-input class="col-12 col-md-6" v-model="fields.cost_price" label="Cost Price" type="number"
              :error-message="errors.cost_price" :error="!!errors.cost_pcoderice" />
            <q-input v-model="fields.selling_price" label="Selling Price" class="col-12 col-md-6"
              :error-message="errors.selling_price" :error="!!errors.selling_price" type="number" />
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete class="q-full-width" label="Brand" v-model="fields.brand"
                :options="formDefaults.collections?.brands"
                :modal-component="checkPermissions('BrandCreate') ? BrandForm : null" :error="errors.brand" />
            </div>
          </div>
          <div>
            <q-input v-model="fields.description" label="Description" class="col-6" :error-message="errors.description"
              :error="!!errors.description" type="textarea" />
          </div>
          <q-card class="q-pa-lg">
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <n-auto-complete class="q-full-width" label="Category" v-model="fields.category"
                  :options="formDefaults.collections?.inventory_categories"
                  :modal-component="checkPermissions('InventoryCategoryCreate') ? InventoryCategoryForm : null"
                  :error="errors.category" @update:modelValue="setCategory" />
              </div>
            </div>
            <div v-if="fields.extra_fields">
              <q-input v-for="(field, index) in fields.extra_fields" :label="field.name" :type="field.type.value"
                :key="index" v-model="fields.extra_data[field.name]"></q-input>
            </div>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <n-auto-complete class="q-full-width" label="Unit" v-model="fields.unit_id"
                  :options="formDefaults.collections?.units"
                  :modal-component="checkPermissions('UnitCreate') ? UnitForm : null" :error="errors.unit_id" />
              </div>
              <div class="col-12 col-md-6">
                <n-auto-complete class="q-full-width" label="Tax Scheme" v-model="fields.tax_scheme_id"
                  :options="formDefaults.collections?.tax_scheme"
                  :modal-component="checkPermissions('TaxSchemeCreate') ? TaxForm : null" :error="errors.tax_scheme_id" />
              </div>
            </div>
            <div>
              <select-item-accounts-with-types v-model="fields.sales_account" label="Sales"
                :options="formDefaults.collections?.sales_accounts" :itemName="fields.name"
                :activeCategory="fields.category"
                :inventory_categories="formDefaults.collections?.inventory_categories" />
              <select-item-accounts-with-types v-model="fields.purchase_account" label="Purchase"
                :options="formDefaults.collections?.purchase_accounts" :itemName="fields.name"
                :activeCategory="fields.category"
                :inventory_categories="formDefaults.collections?.inventory_categories" />
              <select-item-accounts-with-types v-model="fields.discount_allowed_account" label="Discount Allowed"
                :options="formDefaults.collections?.discount_allowed_accounts" :itemName="fields.name"
                :activeCategory="fields.category"
                :inventory_categories="formDefaults.collections?.inventory_categories" />
              <select-item-accounts-with-types v-model="fields.discount_received_account" label="Discount Received"
                :options="formDefaults.collections?.discount_received_accounts" :itemName="fields.name"
                :activeCategory="fields.category"
                :inventory_categories="formDefaults.collections?.inventory_categories" />
            </div>
            <div class="row q-gutter-y-lg q-mt-lg">
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox v-model="fields.track_inventory" label="Track Inventory"
                  :error-message="errors.track_inventory" :error="!!errors.track_inventory" />
              </div>
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox v-model="fields.can_be_sold" label="Can be sold?" :error-message="errors.can_be_sold"
                  :error="!!errors.can_be_sold" :disable="fields.direct_expense || fields.indirect_expense" />
              </div>
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox class="col-4" v-model="fields.can_be_purchased" label="Can be purchased?"
                  :error-message="errors.can_be_purchased" :error="!!errors.can_be_purchased"
                  :disable="fields.direct_expense || fields.indirect_expense" />
              </div>
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox class="col-4" v-model="fields.fixed_asset" label="Fixed Assets"
                  :error-message="errors.fixed_asset" :error="!!errors.fixed_asset"
                  :disable="fields.direct_expense || fields.indirect_expense" />
              </div>
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox class="col-4" v-model="fields.direct_expense" label="Direct Expenses"
                  :error-message="errors.direct_expense" :error="!!errors.direct_expense"
                  @click="toggleExpenses('indirect_expense')" />
              </div>
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox class="col-4" v-model="fields.indirect_expense" label="Indirect Expense?"
                  :error-message="errors.indirect_expense" :error="!!errors.indirect_expense"
                  @click="toggleExpenses('direct_expense')" />
              </div>
            </div>
          </q-card>
          <div class="row justify-between q-pa-sm q-mt-md">
            <div class="col-sm-5 col-12 row q-col-gutter-md items-end" v-if="typeof fields.front_image === 'string' && fields.front_image
              ">
              <div>Front Image</div>
              <div>
                <q-btn target="_blank" class="info" color="blue" :href="fields.front_image">PREVIEW</q-btn>
              </div>
              <div>
                <q-btn color="orange-7" class="ml-5" style="cursor: pointer" @click="clear('front_image')">clear</q-btn>
              </div>
            </div>
            <div v-else class="col-sm-5 col-12">
              <q-file v-model="images.front_image" class="q-full-width" :error-messages="errors.front_image"
                label="Front Image" @update:model-value="
                  onFileChange(fields, $event, 'front_image')
                  ">
                <template v-slot:prepend>
                  <q-icon name="attach_file" />
                </template>
              </q-file>
            </div>
            <div class="col-sm-5 col-12 row q-col-gutter-md items-end"
              v-if="typeof fields.back_image === 'string' && fields.back_image">
              <div>Back Image</div>
              <div>
                <q-btn target="_blank" class="info" color="blue" :href="fields.back_image">PREVIEW</q-btn>
              </div>
              <div>
                <q-btn color="orange-7" class="ml-5" style="cursor: pointer" @click="clear('back_image')">clear</q-btn>
              </div>
            </div>
            <div v-else class="col-sm-5 col-12">
              <q-file v-model="fields.back_image" class="q-full-width" :error-messages="errors.back_image"
                label="Back Image" @update:model-value="onFileChange(fields, $event, 'back_image')">
                <template v-slot:prepend>
                  <q-icon name="attach_file" />
                </template>
              </q-file>
            </div>
          </div>
        </q-card-section>
        <div class="q-mt-lg text-right q-pr-md q-pb-lg">
          <q-btn :loading="loading" v-if="checkPermissions('ItemCreate') && !isEdit" @click.prevent="submitForm"
            color="green" label="Create" class="q-ml-auto q-px-xl" type="submit" />
          <q-btn :loading="loading" v-if="checkPermissions('ItemModify') && isEdit" @click.prevent="submitForm"
            color="green" label="Update" class="q-ml-auto q-px-xl" type="submit" />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script setup>
import NAutoComplete from 'src/components/NAutoComplete.vue'
import BrandForm from 'src/pages/inventory/product/brand/BrandForm.vue'
import InventoryCategoryForm from 'src/pages/inventory/product/category/InventoryCategoryForm.vue'
import TaxForm from 'src/pages/tax/scheme/TaxForm.vue'
import UnitForm from 'src/pages/inventory/unit/UnitForm.vue'
import checkPermissions from 'src/composables/checkPermissions'
const emit = defineEmits([])
const accountTypeValues = ref({
  sales_account: 'dedicated',
  purchase_account: 'dedicated',
  discount_allowed_account: 'dedicated',
  discount_received_account: 'dedicated'
})

const toggleExpenses = (type) => {
  fields.value[type] = false
}
const images = ref({
  front_image: null,
  back_image: null,
})
const endpoint = '/v1/items/'
const { fields, errors, isEdit, formDefaults, submitForm, loading } = useForm(endpoint, {
  getDefaults: true,
  successRoute: '/items/list/',
})
useMeta(() => {
  return {
    title: (isEdit?.value ? 'Items Update' : 'Items Add') + ' | Awecount',
  }
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
fields.value.track_inventory = false
fields.value.can_be_sold = false
fields.value.fixed_asset = false
fields.value.can_be_purchased = false
fields.value.direct_expense = false
fields.value.indirect_expense = false
fields.value.extra_fields = []
fields.value.extra_data = null

const getOptionCollection = (collections, name) => {
  if (collections) {
    let option = collections.find(item => {
      if (item.name === name && item.default) {
        return item;
      }
    });
    if (option) {
      return option.id;
    }
  }
}

const setCategory = () => {
  let category_id = fields.value.category
  if (category_id) {
    const selected = formDefaults.value.collections.inventory_categories.find(item => {
      if (item.id === category_id) {
        return item;
      }
    });
    if (selected.hasOwnProperty("extra_fields")) {
      if (fields.value.extra_data === null) {
        fields.value.extra_data = {}
      }
      if (selected.extra_fields && selected.extra_fields.length) {
        fields.value.extra_fields = selected.extra_fields
        selected.extra_fields.forEach(item => {
          const { extra_data } = fields.value
          fields.value.extra_data[item.name.toLowerCase()] = null
          if (!Object.keys(extra_data).includes(item.name.toLowerCase())) {
            fields.value.extra_data[item.name] = null
          }
        })
      } else {
        fields.value.extra_data = null
        fields.value.extra_fields = null
      }
    }
    if (selected.hasOwnProperty("default_unit_id")) {
      if (selected.default_unit_id) {
        fields.value.unit_id = selected.default_unit_id
      } else {
        fields.value.unit_id = ""
      }
    }

    if (selected.hasOwnProperty("default_tax_scheme_id")) {
      if (selected.default_tax_scheme_id) {
        fields.value.tax_scheme_id = selected.default_tax_scheme_id
      } else {
        fields.value.tax_scheme_id = ""
      }
    }
    if (
      !fields.value.sales_account &&
      selected.hasOwnProperty("items_sales_account_type")
    ) {
      if (selected.items_sales_account_type === "category") {
        fields.value.sales_account = selected.sales_account
      }
      if (selected.items_sales_account_type === "global") {
        fields.value.sales_account = getOptionCollection(formDefaults.value.collections.sales_accounts, "Sales Account")
      }
    }
    if (
      !fields.value.purchase_account &&
      selected.hasOwnProperty("items_purchase_account_type")
    ) {
      if (selected.items_purchase_account_type === "category") {
        fields.value.purchase_account = selected.purchase_account
      }
      if (selected.items_purchase_account_type === "global") {
        fields.value.purchase_account = getOptionCollection(formDefaults.value.collections.purchase_accounts, "Purchase Account")
      }
    }
    if (
      !fields.value.discount_allowed_account &&
      selected.hasOwnProperty("items_discount_allowed_account_type")
    ) {
      if (selected.items_discount_allowed_account_type === "category") {
        fields.value.discount_allowed_account = selected.discount_allowed_account
      }
      if (selected.items_discount_allowed_account_type === "global") {
        fields.value.discount_allowed_account = getOptionCollection(formDefaults.value.collections.discount_allowed_accounts, "Discount Expenses")
      }
    }
    if (
      !fields.value.discount_received_account &&
      selected.hasOwnProperty("items_discount_received_account_type")
    ) {
      if (selected.items_discount_received_account_type === "category") {
        fields.value.discount_received_account = selected.discount_received_account
      }
      if (selected.items_discount_received_account_type === "global") {
        fields.value.discount_received_account = getOptionCollection(formDefaults.value.collections.discount_received_account, "Discount Income")
      }
    }

    if (selected.hasOwnProperty("track_inventory")) {
      fields.value.track_inventory = selected.track_inventory
    }
    if (selected.hasOwnProperty("can_be_sold")) {
      fields.value.can_be_sold = selected.can_be_sold
    }
    if (selected.hasOwnProperty("can_be_purchased")) {
      fields.value.can_be_purchased = selected.can_be_purchased
    }
    if (selected.hasOwnProperty("fixed_asset")) {
      fields.value.fixed_asset = selected.fixed_asset
    }
    if (selected.hasOwnProperty("direct_expense")) {
      fields.value.direct_expense = selected.direct_expense
    }
    if (selected.hasOwnProperty("indirect_expense")) {
      fields.value.indirect_expense = selected.indirect_expense
    }
  }
}
watch(() => accountTypeValues.value.sales_account, (newValue) => {
  // debugger
  if (accountTypeValues.value.sales_account === "category") {
    if (fields.value.category) {
      const selected = formDefaults.value.collections.inventory_categories.find(item => {
        if (item.id === fields.value.category) {
          return item;
        }
      })
      if (selected) fields.value.sales_account = selected.sales_account
    }
  }
  else if (accountTypeValues.value.sales_account === "global") {
    fields.value.sales_account = getOptionCollection(formDefaults.value.collections.sales_accounts, "Sales Account")
  }
  else {
    fields.value.sales_account = null
  }
})
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
}</style>