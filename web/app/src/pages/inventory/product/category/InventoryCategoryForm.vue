<template>
  <q-form class="q-pa-lg" autofocus>
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
            <q-input class="col-12 col-md-6" v-model="fields.name" label="Name" :error-message="errors.name"
              :error="!!errors.name" />
            <q-input v-model="fields.code" label="Code" class="col-12 col-md-6" :error-message="errors.code"
              :error="!!errors.code" />
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-6">
              <n-auto-complete class="q-full-width" label="Unit" v-model="fields.default_unit_id"
                :options="formDefaults.collections?.units"
                :modal-component="checkPermissions('UnitCreate') ? UnitForm : null" :error="errors.default_unit_id" />
            </div>
            <div class="col-12 col-md-6">
              <n-auto-complete class="q-full-width" label="Tax Scheme" v-model="fields.default_tax_scheme_id"
                :options="formDefaults.collections?.tax_scheme"
                :modal-component="checkPermissions('TaxSchemeCreate') ? TaxForm : null"
                :error="errors.default_tax_scheme_id" />
            </div>
          </div>
          <div>
            <select-item-accounts-with-types v-if="fields.can_be_sold" v-model:modelValue="fields.sales_account"
              v-model:typeModelValue="fields.items_sales_account_type" label="Sales"
              :options="formDefaults.collections?.accounts" :itemName="fields.name" :usedInCategoryForm="true" :dedicatedAccount="fields.dedicated_sales_account"/>
          </div>
          <div>
            <select-item-accounts-with-types v-if="fields.can_be_purchased" v-model:modelValue="fields.purchase_account"
              v-model:typeModelValue="fields.items_purchase_account_type" label="Purchase"
              :options="formDefaults.collections?.accounts" :itemName="fields.name" :usedInCategoryForm="true" :dedicatedAccount="fields.dedicated_purchase_account" />
          </div>
          <div>
              <select-item-accounts-with-types v-if="fields.can_be_sold" v-model:modelValue="fields.discount_allowed_account"
                v-model:typeModelValue="fields.items_discount_allowed_account_type" label="Discount Allowed"
                :options="formDefaults.collections?.discount_allowed_accounts" :itemName="fields.name"
                :usedInCategoryForm="true" :dedicatedAccount="fields.discount_allowed_account" />
            </div>
            <div class="col-12 col-lg-6">
              <select-item-accounts-with-types v-if="fields.can_be_purchased" v-model:modelValue="fields.discount_received_account"
                v-model:typeModelValue="fields.items_discount_received_account_type" label="Discount Received"
                :options="formDefaults.collections?.discount_received_accounts" :itemName="fields.name"
                :usedInCategoryForm="true" :dedicatedAccount="fields.discount_received_account" />
          </div>
          <div class="row q-gutter-y-lg q-mt-lg">
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox v-model="fields.track_inventory" label="Track Inventory" :error-message="errors.track_inventory"
                :error="!!errors.track_inventory" />
            </div>
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox v-model="fields.can_be_sold" label="Can be sold?" :error-message="errors.can_be_sold"
                :error="!!errors.can_be_sold" :disable="fields.direct_expense || fields.indirect_expense" />
            </div>
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox v-model="fields.can_be_purchased" label="Can be purchased?"
                :error-message="errors.can_be_purchased" :error="!!errors.can_be_purchased"
                :disable="fields.direct_expense || fields.indirect_expense" />
            </div>
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox v-model="fields.fixed_asset" label="Fixed Asset?" :error-message="errors.fixed_asset"
                :error="!!errors.fixed_asset" :disable="fields.direct_expense || fields.indirect_expense" />
            </div>
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox v-model="fields.direct_expense" label="Direct Expenses" :error-message="errors.direct_expense"
                :error="!!errors.direct_expense" @click="toggleExpenses('indirect_expense')" />
            </div>
            <div class="col-sm-6 col-12 col-lg-4">
              <q-checkbox v-model="fields.indirect_expense" label="Indirect Expense?"
                :error-message="errors.indirect_expense" :error="!!errors.indirect_expense"
                @click="toggleExpenses('direct_expense')" />
            </div>
          </div>
          <div class="row q-my-lg justify-between q-col-gutter-sm">
            <div class="col-12 col-md-6 field-height">
              <div v-if="fields.fixed_asset ||
                fields.direct_expense ||
                fields.indirect_expense
                ">
                <q-select v-model="fields.account_category" :options="parent_account_categories" label="Account Category"
                  option-value="id" option-label="name" map-options emit-value />
              </div>
            </div>
            <div class="col-12 col-md-6 row item-center field-height">
              <q-checkbox v-model="fields.use_account_subcategory" :label="fields.id
                ? 'Use Account Subcategory?'
                : 'Create Account Subcategory?'
                " :error-message="errors.indirect_expense" :error="!!errors.indirect_expense" />
            </div>
          </div>
          <div>
            <div>
              <span class="q-mr-md">Extra Fields</span><q-btn @click="addExtraFields"
                class="bg-primary text-white q-py-none q-px-sm" icon="add"></q-btn>
            </div>
            <div v-if="fields.extra_fields?.length > 0">
              <div class="row q-gutter-x-md items-center" v-for="(field, index) in fields.extra_fields" :key="index">
                <q-input class="col-4" v-model="field.name" label="Name" />
                <q-select class="col-3" v-model="field.type" :options="extraFieldTypes" label="Type" />
                <q-checkbox class="2" v-model="field.enable_search" label="Enable Search?" />
                <!-- <q-btn icon="delete"></q-btn> -->
                <span class="col-1">
                  <q-icon @click="removeExtraFields(index)" class="deleteIcon cursor-pointer" color="red-6" size="sm"
                    name="delete"></q-icon>
                </span>
              </div>
            </div>
          </div>
        </q-card-section>
        <div class="q-mt-lg text-right q-pr-md q-pb-lg">
          <q-btn v-if="checkPermissions('InventoryCategoryModify') && isEdit" :loading="loading"
            @click.prevent="submitForm" color="green" label="Update" class="q-ml-auto q-px-xl" type="submit" />
          <q-btn v-if="checkPermissions('InventoryCategoryCreate') && !isEdit" :loading="loading"
            @click.prevent="submitForm" color="green" label="Create" class="q-ml-auto q-px-xl" type="submit" />
        </div>
      </q-card>
    </q-card>
  </q-form>
</template>

<script setup>
import NAutoComplete from 'src/components/NAutoComplete.vue'
import UnitForm from 'src/pages/inventory/unit/UnitForm.vue'
import TaxForm from 'src/pages/tax/scheme/TaxForm.vue'
import checkPermissions from 'src/composables/checkPermissions'
const emit = defineEmits([])
const extraFieldTypes = [
  { value: 'Text', label: 'Text' },
  { value: 'Number', label: 'Number' },
  { value: 'Date', label: 'Date' },
  { value: 'Choices', label: 'Choices' },
  { value: 'Long', label: 'Long Text' },
]
const account_types = [
  { value: 'dedicated', label: 'Use Dedicated Account' },
  { value: 'category', label: "Use Category's Account" },
  { value: 'global', label: 'Use Global Account' },
]
const toggleExpenses = (type) => {
  fields.value[type] = false
}
const endpoint = '/v1/inventory-categories/'
const { fields, errors, isEdit, formDefaults, submitForm, loading } = useForm(endpoint, {
  getDefaults: true,
  successRoute: '/inventory-category/list/',
})
useMeta(() => {
  return {
    title:
      (isEdit?.value ? 'Update ' : 'Add ') +
      'Inventory Category' +
      ' | Awecount',
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
  if (
    fields.value.extra_fields === null ||
    fields.value.extra_fields === undefined
  ) {
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

.field-height {
  height: 60px;
}

.deleteIcon {
  width: 100px;
}

/* .q-checkbox.disabled {
  color: lightgrey;
  opacity: 0.5;
} */
</style>
