<script setup>
import NAutoComplete from 'src/components/NAutoComplete.vue'
import checkPermissions from 'src/composables/checkPermissions'
import BrandForm from 'src/pages/inventory/product/brand/BrandForm.vue'
import InventoryCategoryForm from 'src/pages/inventory/product/category/InventoryCategoryForm.vue'
import UnitForm from 'src/pages/inventory/unit/UnitForm.vue'
import TaxForm from 'src/pages/tax/scheme/TaxForm.vue'

const route = useRoute()
const $q = useQuasar()
const toggleExpenses = (type) => {
  fields.value[type] = false
}
const images = ref({
  front_image: null,
  back_image: null,
})
const endpoint = `/api/company/${route.params.company}/items/`
const injectUnitObj = ref(null)
const staticOptions = ref({
  sales: null,
  purchase: null,
  discount_allowed: null,
  discount_received: null,
})
const activeInventoryCategory = ref(null)
const { fields, errors, isEdit, formDefaults, submitForm, loading } = useForm(endpoint, {
  getDefaults: true,
  successRoute: `/${route.params.company}/inventory/items`,
})
fields.value.sales_account_type = 'dedicated'
fields.value.purchase_account_type = 'dedicated'
fields.value.discount_allowed_account_type = 'dedicated'
fields.value.discount_received_account_type = 'dedicated'
useMeta(() => {
  return {
    title: `${isEdit?.value ? 'Items Update' : 'Items Add'} | Awecount`,
  }
})
const isExpenses = computed(() => fields.value.direct_expense || fields.value.indirect_expense)

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
  const reader = new FileReader()
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
const clear = field => (fields.value[field] = null)
fields.value.track_inventory = false
fields.value.can_be_sold = false
fields.value.fixed_asset = false
fields.value.can_be_purchased = false
fields.value.direct_expense = false
fields.value.indirect_expense = false
fields.value.extra_fields = []
fields.value.extra_data = null

const setCategory = (selected) => {
  activeInventoryCategory.value = selected
  if (!selected) return
  if (selected.hasOwnProperty('extra_fields')) {
    if (fields.value.extra_data === null) {
      fields.value.extra_data = {}
    }
    if (selected.extra_fields && selected.extra_fields.length) {
      fields.value.extra_fields = selected.extra_fields
      selected.extra_fields.forEach((item) => {
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
  if (selected.hasOwnProperty('default_unit_id')) {
    if (selected.default_unit_id) {
      fields.value.unit_id = selected.default_unit_id
      injectUnitObj.value = selected.selected_unit_obj
    } else {
      fields.value.unit_id = ''
      injectUnitObj.value = null
    }
  }
  if (selected.hasOwnProperty('default_tax_scheme_id')) {
    if (selected.default_tax_scheme_id) {
      fields.value.tax_scheme_id = selected.default_tax_scheme_id
    } else {
      fields.value.tax_scheme_id = ''
    }
  }
  if (!fields.value.sales_account && !fields.value.items_sales_account_type && selected.hasOwnProperty('items_sales_account_type')) {
    if (selected.items_sales_account_type === 'category') {
      fields.value.sales_account = selected.dedicated_sales_account
      staticOptions.value.sales = selected.sales_account_obj
    } else if (selected.items_sales_account_type === 'global') {
      fields.value.sales_account = formDefaults.value.options?.global_accounts?.sales_account_id
    } else if (selected.items_sales_account_type === 'existing') {
      fields.value.sales_account = selected.sales_account
      staticOptions.value.sales = selected.sales_account_obj
    }
    if (selected.items_sales_account_type !== 'creation') {
      fields.value.sales_account_type = selected.items_sales_account_type
    }
  }
  if (!fields.value.purchase_account && !fields.value.items_purchase_account_type && selected.hasOwnProperty('items_purchase_account_type')) {
    if (selected.items_purchase_account_type === 'category') {
      fields.value.purchase_account = selected.dedicated_purchase_account
      staticOptions.value.purchase = selected.purchase_account_obj
    } else if (selected.items_purchase_account_type === 'global') {
      fields.value.purchase_account = formDefaults.value.options?.global_accounts?.purchase_account_id
    } else if (selected.items_purchase_account_type === 'existing') {
      fields.value.purchase_account = selected.purchase_account
      staticOptions.value.purchase = selected.purchase_account_obj
    }
    if (selected.items_purchase_account_type !== 'creation') {
      fields.value.purchase_account_type = selected.items_purchase_account_type
    }
  }
  if (!fields.value.discount_allowed_account && !fields.value.items_discount_allowed_account_type && selected.hasOwnProperty('items_discount_allowed_account_type')) {
    if (selected.items_discount_allowed_account_type === 'category') {
      fields.value.discount_allowed_account = selected.dedicated_discount_allowed_account
      staticOptions.value.discount_allowed = selected.discount_allowed_account_obj
    } else if (selected.items_discount_allowed_account_type === 'global') {
      fields.value.discount_allowed_account = formDefaults.value.options?.global_accounts?.discount_allowed_account_id
    } else if (selected.items_discount_allowed_account_type === 'existing') {
      fields.value.discount_allowed_account = selected.discount_allowed_account
      staticOptions.value.discount_allowed = selected.discount_allowed_account_obj
    }
    if (selected.items_discount_allowed_account_type !== 'creation') {
      fields.value.discount_allowed_account_type = selected.items_discount_allowed_account_type
    }
  }
  if (!fields.value.discount_received_account && !fields.value.items_discount_received_account_type && selected.hasOwnProperty('items_discount_received_account_type')) {
    if (selected.items_discount_received_account_type === 'category') {
      fields.value.discount_received_account = selected.dedicated_discount_received_account
      staticOptions.value.discount_received = selected.discount_received_account_obj
    } else if (selected.items_discount_received_account_type === 'global') {
      fields.value.discount_received_account = formDefaults.value.options?.global_accounts?.discount_received_account_id
    } else if (selected.items_discount_received_account_type === 'existing') {
      fields.value.discount_received_account = selected.discount_received_account
      staticOptions.value.discount_received = selected.discount_received_account_obj
    }
    if (selected.items_discount_received_account_type !== 'creation') {
      fields.value.discount_received_account_type = selected.items_discount_received_account_type
    }
  }

  if (selected.hasOwnProperty('track_inventory')) {
    fields.value.track_inventory = selected.track_inventory
  }
  if (selected.hasOwnProperty('can_be_sold')) {
    fields.value.can_be_sold = selected.can_be_sold
  }
  if (selected.hasOwnProperty('can_be_purchased')) {
    fields.value.can_be_purchased = selected.can_be_purchased
  }
  if (selected.hasOwnProperty('fixed_asset')) {
    fields.value.fixed_asset = selected.fixed_asset
  }
  if (selected.hasOwnProperty('direct_expense')) {
    fields.value.direct_expense = selected.direct_expense
  }
  if (selected.hasOwnProperty('indirect_expense')) {
    fields.value.indirect_expense = selected.indirect_expense
  }
}

const onTypeUpdate = (key, selectedType) => {
  if (errors.value && errors.value.hasOwnProperty(key)) {
    delete errors.value[key]
  }
  if (selectedType === 'category' && !fields.value.category) {
    $q.notify({
      color: 'orange-6',
      message: 'Please select a category first!',
      icon: 'report_problem',
      position: 'top-right',
    })
  }
}

watch(
  () => fields.value.can_be_purchased,
  (newValue) => {
    if (newValue) {
      fields.value.purchase_account_type || (fields.value.purchase_account_type = 'dedicated')
      fields.value.discount_received_account_type || (fields.value.discount_received_account_type = 'dedicated')
    }
  },
)
watch(
  () => fields.value.can_be_sold,
  (newValue) => {
    if (newValue) {
      fields.value.sales_account_type || (fields.value.sales_account_type = 'dedicated')
      fields.value.discount_allowed_account_type || (fields.value.discount_allowed_account_type = 'dedicated')
    }
  },
)
watch(
  () => fields.value,
  (newValue) => {
    // Run when from loads
    if (newValue) {
      if (newValue.selected_unit_obj) {
        injectUnitObj.value = newValue.selected_unit_obj
        if (['category', 'existing'].includes(newValue.sales_account_type)) {
          staticOptions.value.sales = newValue.selected_sales_account_obj
        }
        if (['category', 'existing'].includes(newValue.purchase_account_type)) {
          staticOptions.value.purchase = newValue.selected_purchase_account_obj
        }
        if (['category', 'existing'].includes(newValue.discount_allowed_account_type)) {
          staticOptions.value.discount_allowed = newValue.selected_discount_allowed_account_obj
        }
        if (['category', 'existing'].includes(newValue.discount_received_account_type)) {
          staticOptions.value.discount_received = newValue.selected_discount_received_account_obj
        }
      }
    }
  },
)
</script>

<template>
  <q-form autofocus class="q-pa-lg">
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
            <q-input
              v-model="fields.name"
              class="col-12 col-md-6"
              label="Name *"
              :error="!!errors.name"
              :error-message="errors.name"
            />
            <q-input
              v-model="fields.code"
              class="col-12 col-md-6"
              label="Code"
              :error="!!errors.code"
              :error-message="errors.code"
            />
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model.number="fields.cost_price"
              class="col-12 col-md-6"
              label="Cost Price"
              type="number"
              :error="!!errors.cost_price"
              :error-message="errors.cost_price"
            />
            <q-input
              v-model.number="fields.selling_price"
              class="col-12 col-md-6"
              label="Selling Price"
              type="number"
              :error="!!errors.selling_price"
              :error-message="errors.selling_price"
            />
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete-v2
                v-model="fields.brand"
                label="Brand"
                :endpoint="`/api/company/${$route.params.company}/items/create-defaults/brands`"
                :error="errors.brand"
                :modal-component="checkPermissions('brand.create') ? BrandForm : null"
                :options="formDefaults.collections?.brands"
                :static-option="fields.selected_brand_obj"
              />
            </div>
          </div>
          <div>
            <q-input
              v-model="fields.description"
              class="col-6"
              label="Description"
              type="textarea"
              :error="!!errors.description"
              :error-message="errors.description"
            />
          </div>
          <q-card class="q-pa-lg">
            <div v-if="isEdit ? fields.hasOwnProperty('selected_inventory_category_obj') : true" class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <n-auto-complete-v2
                  v-model="fields.category"
                  label="Category"
                  :emit-obj="true"
                  :endpoint="`/api/company/${$route.params.company}/items/create-defaults/inventory_categories`"
                  :error="errors.category"
                  :modal-component="checkPermissions('inventorycategory.create') ? InventoryCategoryForm : null"
                  :options="formDefaults.collections?.inventory_categories"
                  :static-option="fields.selected_inventory_category_obj"
                  @update-obj="setCategory"
                />
              </div>
            </div>
            <div v-if="fields.extra_data">
              <q-input
                v-for="(field, index) in fields.extra_fields"
                :key="index"
                v-model="fields.extra_data[field.name]"
                :label="field.name"
                :type="field.type.value"
              />
            </div>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-md-6">
                <n-auto-complete-v2
                  v-model="fields.unit_id"
                  label="Unit"
                  :endpoint="`/api/company/${$route.params.company}/items/create-defaults/units`"
                  :error="errors.unit_id"
                  :modal-component="checkPermissions('unit.create') ? UnitForm : null"
                  :options="formDefaults.collections?.units"
                  :static-option="injectUnitObj"
                />
              </div>
              <div class="col-12 col-md-6">
                <NAutoComplete
                  v-model="fields.tax_scheme_id"
                  label="Tax Scheme"
                  :error="errors.tax_scheme_id"
                  :modal-component="checkPermissions('taxscheme.create') ? TaxForm : null"
                  :options="formDefaults.collections?.tax_scheme"
                />
              </div>
            </div>
            <div class="row q-gutter-y-lg q-mt-lg">
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox
                  v-model="fields.track_inventory"
                  label="Track Inventory"
                  :error="!!errors.track_inventory"
                  :error-message="errors.track_inventory"
                />
              </div>
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox
                  v-model="fields.can_be_sold"
                  label="Can be sold?"
                  :disable="fields.direct_expense || fields.indirect_expense"
                  :error="!!errors.can_be_sold"
                  :error-message="errors.can_be_sold"
                />
              </div>
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox
                  v-model="fields.can_be_purchased"
                  class="col-4"
                  label="Can be purchased?"
                  :disable="fields.direct_expense || fields.indirect_expense"
                  :error="!!errors.can_be_purchased"
                  :error-message="errors.can_be_purchased"
                />
              </div>
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox
                  v-model="fields.fixed_asset"
                  class="col-4"
                  label="Fixed Assets"
                  :disable="fields.direct_expense || fields.indirect_expense"
                  :error="!!errors.fixed_asset"
                  :error-message="errors.fixed_asset"
                />
              </div>
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox
                  v-model="fields.direct_expense"
                  class="col-4"
                  label="Direct Expenses"
                  :error="!!errors.direct_expense"
                  :error-message="errors.direct_expense"
                  @click="toggleExpenses('indirect_expense')"
                />
              </div>
              <div class="col-md-6 col-12 col-lg-4">
                <q-checkbox
                  v-model="fields.indirect_expense"
                  class="col-4"
                  label="Indirect Expense?"
                  :error="!!errors.indirect_expense"
                  :error-message="errors.indirect_expense"
                  @click="toggleExpenses('direct_expense')"
                />
              </div>
            </div>
            <div class="mt-4">
              <select-item-accounts-with-types
                v-if="fields.can_be_sold"
                v-model:model-value="fields.sales_account"
                v-model:type-model-value="fields.sales_account_type"
                label="Sales"
                :active-category="fields.category"
                :active-category-obj="activeInventoryCategory || fields.selected_inventory_category_obj"
                :dedicated-account="fields.dedicated_sales_account"
                :default-category-name="fields.selected_category_name"
                :error="errors.sales_account"
                :global-accounts="formDefaults.options?.global_accounts"
                :item-name="fields.name"
                :options="formDefaults.collections?.accounts"
                :static-option="staticOptions.sales"
                @update:type-model-value="(value) => onTypeUpdate('sales_account', value)"
              />
              <select-item-accounts-with-types
                v-if="fields.can_be_purchased"
                v-model:model-value="fields.purchase_account"
                v-model:type-model-value="fields.purchase_account_type"
                label="Purchase"
                :active-category="fields.category"
                :active-category-obj="activeInventoryCategory || fields.selected_inventory_category_obj"
                :dedicated-account="fields.dedicated_purchase_account"
                :error="errors.purchase_account"
                :global-accounts="formDefaults.options?.global_accounts"
                :item-name="fields.name"
                :options="formDefaults.collections?.accounts"
                :static-option="staticOptions.purchase"
                @update:type-model-value="(value) => onTypeUpdate('purchase_account', value)"
              />
              <select-item-accounts-with-types
                v-if="fields.can_be_sold"
                v-model:model-value="fields.discount_allowed_account"
                v-model:type-model-value="fields.discount_allowed_account_type"
                label="Discount Allowed"
                :active-category="fields.category"
                :active-category-obj="activeInventoryCategory || fields.selected_inventory_category_obj"
                :dedicated-account="fields.dedicated_discount_allowed_account"
                :error="errors.discount_allowed_account"
                :global-accounts="formDefaults.options?.global_accounts"
                :item-name="fields.name"
                :options="formDefaults.collections?.accounts"
                :static-option="staticOptions.discount_allowed"
                @update:type-model-value="(value) => onTypeUpdate('discount_allowed_account', value)"
              />
              <select-item-accounts-with-types
                v-if="fields.can_be_purchased"
                v-model:model-value="fields.discount_received_account"
                v-model:type-model-value="fields.discount_received_account_type"
                label="Discount Received"
                :active-category="fields.category"
                :active-category-obj="activeInventoryCategory || fields.selected_inventory_category_obj"
                :dedicated-account="fields.dedicated_discount_received_account"
                :error="errors.discount_received_account"
                :global-accounts="formDefaults.options?.global_accounts"
                :item-name="fields.name"
                :options="formDefaults.collections?.accounts"
                :static-option="staticOptions.discount_received"
                @update:type-model-value="(value) => onTypeUpdate('discount_received_account', value)"
              />
            </div>
          </q-card>
          <div class="row justify-between q-pa-sm q-mt-md">
            <div v-if="typeof fields.front_image === 'string' && fields.front_image" class="col-sm-5 col-12 row q-col-gutter-md items-end">
              <div>Front Image</div>
              <div>
                <q-btn
                  class="info"
                  color="blue"
                  target="_blank"
                  :href="fields.front_image"
                >
                  PREVIEW
                </q-btn>
              </div>
              <div>
                <q-btn
                  class="ml-5"
                  color="orange-7"
                  style="cursor: pointer"
                  @click="clear('front_image')"
                >
                  clear
                </q-btn>
              </div>
            </div>
            <div v-else class="col-sm-5 col-12">
              <q-file
                v-model="images.front_image"
                label="Front Image"
                :error-messages="errors.front_image"
                @update:model-value="onFileChange(fields, $event, 'front_image')"
              >
                <template #prepend>
                  <q-icon name="attach_file" />
                </template>
              </q-file>
            </div>
            <div v-if="typeof fields.back_image === 'string' && fields.back_image" class="col-sm-5 col-12 row q-col-gutter-md items-end">
              <div>Back Image</div>
              <div>
                <q-btn
                  class="info"
                  color="blue"
                  target="_blank"
                  :href="fields.back_image"
                >
                  PREVIEW
                </q-btn>
              </div>
              <div>
                <q-btn
                  class="ml-5"
                  color="orange-7"
                  style="cursor: pointer"
                  @click="clear('back_image')"
                >
                  clear
                </q-btn>
              </div>
            </div>
            <div v-else class="col-sm-5 col-12">
              <q-file
                v-model="fields.back_image"
                label="Back Image"
                :error-messages="errors.back_image"
                @update:model-value="onFileChange(fields, $event, 'back_image')"
              >
                <template #prepend>
                  <q-icon name="attach_file" />
                </template>
              </q-file>
            </div>
          </div>
        </q-card-section>
        <div class="q-mt-lg text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('item.create') && !isEdit"
            class="q-ml-auto q-px-xl"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="submitForm"
          />
          <q-btn
            v-if="checkPermissions('item.modify') && isEdit"
            class="q-ml-auto q-px-xl"
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
