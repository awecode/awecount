<script setup>
import NAutoComplete from 'src/components/NAutoComplete.vue'
import checkPermissions from 'src/composables/checkPermissions'
import UnitForm from 'src/pages/inventory/unit/UnitForm.vue'
import TaxForm from 'src/pages/tax/scheme/TaxForm.vue'

const route = useRoute()
const extraFieldTypes = [
  { value: 'Text', label: 'Text' },
  { value: 'Number', label: 'Number' },
  { value: 'Date', label: 'Date' },
  { value: 'Choices', label: 'Choices' },
  { value: 'Long', label: 'Long Text' },
]
const toggleExpenses = (type) => {
  fields.value[type] = false
}
const endpoint = `/api/company/${route.params.company}/inventory-categories/`
const { fields, errors, isEdit, formDefaults, submitForm, loading } = useForm(endpoint, {
  getDefaults: true,
  successRoute: `/${route.params.company}/inventory/categories`,
})
fields.value.sales_account_type = 'dedicated'
fields.value.purchase_account_type = 'dedicated'
fields.value.discount_allowed_account_type = 'dedicated'
fields.value.discount_received_account_type = 'dedicated'
useMeta(() => {
  return {
    title: `${isEdit?.value ? 'Update ' : 'Add '}Inventory Category` + ` | Awecount`,
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

const parent_account_categories = computed(() => {
  if (fields.value.fixed_asset) {
    return formDefaults.value.collections.fixed_assets_categories
  }
  if (fields.value.direct_expense) {
    return formDefaults.value.collections.direct_expenses_categories
  }
  if (fields.value.indirect_expense) {
    return formDefaults.value.collections.indirect_expenses_categories
  }
  return []
})
const addExtraFields = () => {
  if (fields.value.extra_fields === null || fields.value.extra_fields === undefined) {
    fields.value.extra_fields = []
  }
  fields.value.extra_fields.push({
    name: null,
    type: null,
    enable_search: false,
  })
}
const removeExtraFields = (idx) => {
  fields.value.extra_fields.splice(idx, 1)
}
fields.value.track_inventory = true
fields.value.can_be_sold = true
fields.value.can_be_purchased = true
fields.value.direct_expense = false
fields.value.fixed_asset = false
fields.value.indirect_expense = false
fields.value.use_account_subcategory = false
fields.value.items_discount_received_account_type = 'dedicated'
fields.value.items_discount_allowed_account_type = 'dedicated'
fields.value.items_sales_account_type = 'dedicated'
fields.value.items_purchase_account_type = 'dedicated'

const onSubmitClick = () => {
  if (fields.value.extra_fields && fields.value.extra_fields.length) {
    fields.value.extra_fields = fields.value.extra_fields.filter(item => item.name && item.type)
  }
  submitForm()
}
</script>

<template>
  <q-form autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span v-if="isEdit">Update {{ fields.name }}</span>
          <span v-else>New Inventory Category</span>
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
            <div class="col-12 col-md-6">
              <n-auto-complete-v2
                v-model="fields.default_unit_id"
                label="Unit"
                :endpoint="`/api/company/${$route.params.company}/inventory-categories/create-defaults/units`"
                :error="errors.default_unit_id"
                :modal-component="checkPermissions('unit.create') ? UnitForm : null"
                :options="formDefaults.collections?.units"
                :static-option="fields.selected_unit_obj"
              />
            </div>
            <div class="col-12 col-md-6">
              <NAutoComplete
                v-model="fields.default_tax_scheme_id"
                label="Tax Scheme"
                :error="errors.default_tax_scheme_id"
                :modal-component="checkPermissions('taxscheme.create') ? TaxForm : null"
                :options="formDefaults.collections?.tax_scheme"
              />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <q-input
              v-model="fields.hs_code"
              class="col-12 col-md-6"
              label="H.S. code"
              :error="!!errors.hs_code"
              :error-message="errors.hs_code"
            />
          </div>
          <div class="row q-gutter-y-lg mt-1 mb-6">
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox
                v-model="fields.track_inventory"
                label="Track Inventory"
                :error="!!errors.track_inventory"
                :error-message="errors.track_inventory"
              />
            </div>
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox
                v-model="fields.can_be_sold"
                label="Can be sold?"
                :disable="fields.direct_expense || fields.indirect_expense"
                :error="!!errors.can_be_sold"
                :error-message="errors.can_be_sold"
              />
            </div>
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox
                v-model="fields.can_be_purchased"
                label="Can be purchased?"
                :disable="fields.direct_expense || fields.indirect_expense"
                :error="!!errors.can_be_purchased"
                :error-message="errors.can_be_purchased"
              />
            </div>
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox
                v-model="fields.fixed_asset"
                label="Fixed Asset?"
                :disable="fields.direct_expense || fields.indirect_expense"
                :error="!!errors.fixed_asset"
                :error-message="errors.fixed_asset"
              />
            </div>
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox
                v-model="fields.direct_expense"
                label="Direct Expenses"
                :error="!!errors.direct_expense"
                :error-message="errors.direct_expense"
                @click="toggleExpenses('indirect_expense')"
              />
            </div>
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox
                v-model="fields.indirect_expense"
                label="Indirect Expense?"
                :error="!!errors.indirect_expense"
                :error-message="errors.indirect_expense"
                @click="toggleExpenses('direct_expense')"
              />
            </div>
          </div>
          <div class="row justify-between q-col-gutter-sm my-4">
            <div class="col-12 col-md-6">
              <div v-if="fields.fixed_asset || fields.direct_expense || fields.indirect_expense">
                <q-select
                  v-model="fields.account_category"
                  emit-value
                  map-options
                  label="Account Category"
                  option-label="name"
                  option-value="id"
                  :options="parent_account_categories"
                />
              </div>
            </div>
          </div>
          <!-- {{ fields.sales_account_obj }} -->
          <div v-if="isEdit ? fields.hasOwnProperty('sales_account_obj') : true">
            <div>
              <select-item-accounts-with-types
                v-if="fields.can_be_sold"
                v-model:model-value="fields.sales_account"
                v-model:type-model-value="fields.items_sales_account_type"
                label="Sales"
                :dedicated-account="fields.dedicated_sales_account"
                :error="errors.sales_account"
                :global-accounts="formDefaults.options?.global_accounts"
                :item-name="fields.name"
                :options="formDefaults.collections?.accounts"
                :static-option="fields.sales_account_obj"
                :used-in-category-form="true"
              />
            </div>
            <div>
              <select-item-accounts-with-types
                v-if="fields.can_be_purchased"
                v-model:model-value="fields.purchase_account"
                v-model:type-model-value="fields.items_purchase_account_type"
                label="Purchase"
                :dedicated-account="fields.dedicated_purchase_account"
                :error="errors.purchase_account"
                :global-accounts="formDefaults.options?.global_accounts"
                :item-name="fields.name"
                :options="formDefaults.collections?.accounts"
                :static-option="fields.purchase_account_obj"
                :used-in-category-form="true"
              />
            </div>
            <div>
              <select-item-accounts-with-types
                v-if="fields.can_be_sold"
                v-model:model-value="fields.discount_allowed_account"
                v-model:type-model-value="fields.items_discount_allowed_account_type"
                label="Discount Allowed"
                :dedicated-account="fields.dedicated_discount_allowed_account"
                :error="errors.discount_allowed_account"
                :global-accounts="formDefaults.options?.global_accounts"
                :item-name="fields.name"
                :options="formDefaults.collections?.discount_allowed_accounts"
                :static-option="fields.discount_allowed_account_obj"
                :used-in-category-form="true"
              />
            </div>
            <div class="col-12 col-lg-6">
              <select-item-accounts-with-types
                v-if="fields.can_be_purchased"
                v-model:model-value="fields.discount_received_account"
                v-model:type-model-value="fields.items_discount_received_account_type"
                label="Discount Received"
                :dedicated-account="fields.dedicated_discount_received_account"
                :error="errors.discount_received_account"
                :global-accounts="formDefaults.options?.global_accounts"
                :item-name="fields.name"
                :options="formDefaults.collections?.discount_received_accounts"
                :static-option="fields.discount_received_account_obj"
                :used-in-category-form="true"
              />
            </div>
          </div>
          <div class="row my-6">
            <div class="col-12 col-md-6 row item-center">
              <q-checkbox
                v-model="fields.use_account_subcategory"
                :error="!!errors.indirect_expense"
                :error-message="errors.indirect_expense"
                :label="fields.id ? 'Use corresponding category in chart of accounts for ledger accounts of items in this category?' : 'Create corresponding category in chart of accounts for ledger accounts of items in this category?'"
              />
            </div>
          </div>
          <div>
            <div>
              <span class="q-mr-md">Extra Fields</span>
              <q-btn class="bg-primary text-white q-py-none q-px-sm" icon="add" @click="addExtraFields" />
            </div>
            <div v-if="fields.extra_fields?.length > 0">
              <div v-for="(field, index) in fields.extra_fields" :key="index" class="row q-gutter-x-md items-center">
                <q-input v-model="field.name" class="col-4" label="Name" />
                <q-select
                  v-model="field.type"
                  class="col-3"
                  label="Type"
                  :options="extraFieldTypes"
                />
                <q-checkbox v-model="field.enable_search" class="2" label="Enable Search?" />
                <!-- <q-btn icon="delete"></q-btn> -->
                <span class="col-1">
                  <q-icon
                    class="deleteIcon cursor-pointer"
                    color="red-6"
                    name="delete"
                    size="sm"
                    @click="removeExtraFields(index)"
                  />
                </span>
              </div>
            </div>
          </div>
        </q-card-section>
        <div class="q-mt-lg text-right q-pr-md q-pb-lg">
          <q-btn
            v-if="checkPermissions('inventorycategory.modify') && isEdit"
            class="q-ml-auto q-px-xl"
            color="green"
            label="Update"
            type="submit"
            :loading="loading"
            @click.prevent="onSubmitClick"
          />
          <q-btn
            v-if="checkPermissions('inventorycategory.create') && !isEdit"
            class="q-ml-auto q-px-xl"
            color="green"
            label="Create"
            type="submit"
            :loading="loading"
            @click.prevent="onSubmitClick"
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

/* .field-height {
  height: 60px;
} */

.deleteIcon {
  width: 100px;
}

/* .q-checkbox.disabled {
  color: lightgrey;
  opacity: 0.5;
} */
</style>
