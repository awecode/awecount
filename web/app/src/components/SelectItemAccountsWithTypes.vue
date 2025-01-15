<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import LedgerForm from 'src/pages/account/ledger/LedgerForm.vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  options: {
    type: Object,
    default: () => {
      return {
        results: [],
        pagination: {},
      }
    },
  },
  error: {
    type: String,
    default: () => '',
  },
  activeCategory: {
    type: [Number, null],
    default: () => null,
  },
  modelValue: {
    type: [Number, null],
    default: () => null,
  },
  typeModelValue: {
    type: [String, null],
    default: () => null,
  },
  itemName: {
    type: String,
    required: false,
  },
  usedInCategoryForm: {
    type: Boolean,
    default: () => false,
  },
  dedicatedAccount: {
    type: [Number, null],
    default: () => null,
  },
  activeCategoryObj: {
    type: [Object, null],
    default: () => null,
  },
  globalAccounts: {
    type: [Object, null],
    default: () => null,
  },
  staticOption: {
    type: [Object, null],
    default: () => null,
  },
  defaultCategoryName: {
    type: String,
    default: () => null,
  },
})
const emits = defineEmits(['update:modelValue', 'update:typeModelValue'])
const route = useRoute()
const $q = useQuasar()
const type = ref(props.typeModelValue)
const modalValue = ref(props.modelValue)
const injectOption = ref(props.staticOption)
const account_types
  = props.usedInCategoryForm
    ? [
        { value: 'dedicated', label: 'Use a dedicated account for the item' },
        { value: 'global', label: 'Use global account' },
        { value: 'category', label: 'Use category-specific account' },
        { value: 'existing', label: 'Choose an existing account' },
        { value: 'creation', label: 'Choose during item creation' },
      ]
    : [
        { value: 'dedicated', label: 'Use a dedicated account' },
        { value: 'global', label: 'Use global account' },
        { value: 'category', label: 'Use category\'s account' },
        { value: 'existing', label: 'Use an existing account' },
      ]
const onTypeChange = (newValue) => {
  if (newValue === 'category' && props.activeCategoryObj) {
    if (!props.usedInCategoryForm) {
      const fieldType = `${props.label.toLowerCase().replaceAll(' ', '_')}_account`
      if (props.activeCategoryObj) {
        modalValue.value = props.activeCategoryObj[fieldType]
      } else {
        modalValue.value = null
        $q.notify({
          color: 'orange-6',
          message: `Selected Category Has no ${fieldType.replaceAll('_', ' ')} !`,
          icon: 'report_problem',
          position: 'top-right',
        })
      }
    } else {
      modalValue.value = null
    }
  } else if (newValue === 'global') {
    modalValue.value = globalAccountObjComputed.value.id
  } else {
    modalValue.value = null
  }
}
watch(
  () => props.modelValue,
  (newValue) => {
    modalValue.value = newValue
  },
)
watch(
  () => props.typeModelValue,
  (newValue) => {
    type.value = newValue
  },
)
watch(
  () => type.value,
  newValue => emits('update:typeModelValue', newValue),
)
watch(
  () => modalValue.value,
  newValue => emits('update:modelValue', newValue),
)
const globalAccountName = {
  'Sales': 'Sales Account',
  'Purchase': 'Purchase Account',
  'Discount Allowed': 'Discount Expenses',
  'Discount Received': 'Discount Income',
}
const globalAcIdKeyMap = {
  'Sales': 'sales_account_id',
  'Purchase': 'purchase_account_id',
  'Discount Allowed': 'discount_allowed_account_id',
  'Discount Received': 'discount_received_account_id',
}
const globalAccountObjComputed = computed(() => {
  const data = {
    id: null,
    name: null,
  }
  if (!props.globalAccounts) return data
  if (props.globalAccounts.hasOwnProperty(globalAcIdKeyMap[props.label])) {
    data.id = props.globalAccounts[globalAcIdKeyMap[props.label]]
    data.name = globalAccountName[props.label]
  }
  return data
})
const dedicatedAccountName = computed(() => {
  if (props.label === 'Sales') return `${props.itemName} (Sales)`
  else if (props.label === 'Purchase') return `${props.itemName} (Purchase)`
  else if (props.label === 'Discount Allowed') return `Discount Allowed - ${props.itemName}`
  else if (props.label === 'Discount Received') return `Discount Received - ${props.itemName}`
  else return ''
})
const categoryAccountNameComputed = computed(() => {
  let categoryName = null
  if (props.activeCategoryObj && props.activeCategory) {
    categoryName = props.activeCategoryObj.name
  } else if (props.activeCategory && props.defaultCategoryName) {
    categoryName = props.defaultCategoryName
  }
  if (!categoryName) return null
  if (props.label === 'Sales') return `${categoryName} (Sales)`
  else if (props.label === 'Purchase') return `${categoryName} (Purchase)`
  else if (props.label === 'Discount Allowed') return `Discount Allowed - ${categoryName}`
  else if (props.label === 'Discount Received') return `Discount Received - ${categoryName}`
  return null
})
const endpointLabelMap = {
  'Sales': `/api/company/${route.params.company}/items/create-defaults/accounts`,
  'Purchase': `/api/company/${route.params.company}/items/create-defaults/accounts`,
  'Discount Allowed': `/api/company/${route.params.company}/items/create-defaults/discount_allowed_accounts`,
  'Discount Received': `/api/company/${route.params.company}/items/create-defaults/discount_received_accounts`,
}
</script>

<template>
  <div class="grid lg:grid-cols-2 lg:gap-4">
    <div>
      <q-select
        v-model="type"
        emit-value
        map-options
        class="q-full-width"
        option-label="label"
        option-value="value"
        :error="false"
        :label="`${label} A/C Options`"
        :options="account_types"
        @update:model-value="onTypeChange"
      />
    </div>
    <div>
      <n-auto-complete-v2
        v-if="type === 'existing'"
        v-model="modalValue"
        class="q-full-width"
        :endpoint="endpointLabelMap[props.label]"
        :error="error"
        :label="`${label} Account`"
        :modal-component="checkPermissions('account.create') ? LedgerForm : null"
        :options="props.options"
        :static-option="injectOption"
      />
      <div v-else-if="type === 'dedicated'" class="h-full w-full items-center" style="display: flex; gap: 10px">
        <div v-if="dedicatedAccount && !usedInCategoryForm" class="w-full">
          <q-input
            v-model="dedicatedAccountName"
            disable
            class="w-full"
            :error="false"
            :label="`${label} Account`"
          />
        </div>
        <div v-else class="flex gap-2 items-center no-wrap">
          <q-icon color="grey-7" name="info" size="sm" />
          <div class="text-grey-7 whitespace-normal">
            A new {{ props.label }} Account will be created for the Item
          </div>
        </div>
      </div>
      <div v-else-if="type === 'category'" class="flex items-center h-full">
        <div v-if="usedInCategoryForm" class="flex gap-2 items-end no-wrap">
          <q-icon color="grey-7" name="info" size="sm" />
          <div class="text-grey-7">
            Category's {{ props.label }} Account will be used for the Item
          </div>
        </div>
        <div v-else class="w-full">
          <q-input
            v-if="modalValue"
            v-model="categoryAccountNameComputed"
            disable
            class="w-full"
            :error="!!error"
            :error-message="error"
            :label="`${label} Account`"
          />
          <q-input
            v-else
            disable
            class="w-full"
            :error="!!error"
            :error-message="error"
            :label="`${label} Account`"
          />
        </div>
      </div>
      <div v-else-if="type === 'creation' && usedInCategoryForm" class="flex items-center gap-2 h-full">
        <q-icon color="grey-7" name="info" size="sm" />
        <div class="text-grey-7">
          You will be able to choose options while creating item.
        </div>
      </div>
      <q-select
        v-else
        v-model="modalValue"
        disable
        emit-value
        map-options
        option-label="name"
        option-value="id"
        :error="!!error"
        :error-message="error"
        :label="`${label} Account`"
        :options="globalAccountObjComputed.id ? [globalAccountObjComputed] : []"
      />
    </div>
  </div>
</template>
