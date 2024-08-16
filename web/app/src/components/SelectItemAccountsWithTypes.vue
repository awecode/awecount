<template>
    <div class="grid lg:grid-cols-2 lg:gap-4">
        <div>
            <q-select class="q-full-width" :label="`${label} A/C Options`" option-value="value" option-label="label"
                map-options emit-value v-model="type" :options="account_types" :error="false" @update:model-value="onTypeChange"/>
        </div>
        <div>
            <n-auto-complete-v2 v-if="type === 'existing'" class="q-full-width" :label="`${label} Account`"
                v-model="modalValue" :options="props.options" :endpoint="endpointLabelMap[props.label]"
                :modal-component="checkPermissions('AccountCreate') ? LedgerForm : null" :error="error" :staticOption="injectOption" />
            <div v-else-if="type === 'dedicated'" class="h-full w-full items-center" style="display: flex; gap: 10px;">
                <div v-if="dedicatedAccount && !usedInCategoryForm" class="w-full">
                  <q-input :label="label + ' Account'" class="w-full" disable :error="false" v-model="dedicatedAccountName"></q-input>
                </div>
                <div v-else class="flex gap-2 items-center no-wrap">
                  <q-icon name="info" size="sm" color="grey-7"></q-icon>
                  <div class="text-grey-7 whitespace-normal">A new {{ props.label }} Account will be created for the Item</div>
                </div>
            </div>
            <div v-else-if="type === 'category'" class="flex items-center h-full">
              <div v-if="usedInCategoryForm" class="flex gap-2 items-end no-wrap">
                <q-icon name="info" size="sm" color="grey-7"></q-icon>
                <div class="text-grey-7">Category's {{ props.label }} Account will be used for the Item</div>
              </div>
              <div v-else class="w-full">
                <q-input v-if="modalValue" :label="`${label} Account`" v-model="categoryAccountNameComputed" class="w-full" disable :error="!!error" :error-message="error"></q-input>
                <q-input v-else :label="`${label} Account`" class="w-full" disable :error="!!error" :error-message="error"></q-input>
              </div>
            </div>
            <div v-else-if="type === 'creation' && usedInCategoryForm" class="flex items-center gap-2 h-full">
              <q-icon name="info" size="sm" color="grey-7"></q-icon>
              <div class="text-grey-7">You will be able to choose options while creating item.</div>
            </div>
            <q-select v-else :label="`${label} Account`" option-value="id" option-label="name" map-options emit-value
                v-model="modalValue" disable :options="globalAccountObjComputed.id ? [globalAccountObjComputed] : []"
                :error="!!error" :error-message="error"></q-select>
        </div>
    </div>
</template>

<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import LedgerForm from 'src/pages/account/ledger/LedgerForm.vue'
const props = defineProps({
    label: {
        type: String,
        required: true
    },
    options: {
        type: Object,
        default: () => {
          return {
            results: [],
            pagination: {}
          }
        }
    },
    error: {
        type: String,
        default: () => ''
    },
    activeCategory: {
        type: [Number, null],
        default: () => null
    },
    modelValue: {
        type: [Number, null],
        default: () => null
    },
    typeModelValue: {
        type: [String, null],
        default: () => null
    },
    itemName: {
        type: String,
        required: false
    },
    usedInCategoryForm: {
        type: Boolean,
        default: () => false
    },
    dedicatedAccount: {
      type: [Number, null],
      default: () => null
    },
    activeCategoryObj: {
      type: [Object, null],
      default: () => null
    },
    globalAccounts: {
      type: [Object, null],
      default: () => null
    },
    staticOption: {
      type: [Object, null],
      default: () => null
    },
    defaultCategoryName: {
      type: String,
      default: () => null
    }
})
const $q = useQuasar()
const emits = defineEmits(['update:modelValue', 'update:typeModelValue'])
const type = ref(props.typeModelValue)
const modalValue = ref(props.modelValue)
const injectOption = ref(props.staticOption)
const account_types = props.usedInCategoryForm ? [
    { value: 'dedicated', label: 'Use a dedicated account for the item' },
    { value: 'global', label: 'Use global account' },
    { value: 'category', label: 'Use category-specific account' },
    { value: 'existing', label: 'Choose an existing account' },
    { value: 'creation', label: 'Choose during item creation' },
] : [
    { value: 'dedicated', label: 'Use a dedicated account' },
    { value: 'global', label: 'Use global account' },
    { value: 'category', label: "Use category's account" },
    { value: 'existing', label: 'Use an existing account' },
]
const onTypeChange = (newValue) => {
  if (newValue === 'category' && props.activeCategoryObj) {
    if (!props.usedInCategoryForm) {
      const fieldType = props.label.toLowerCase().replaceAll(' ', '_') + '_account'
      if (props.activeCategoryObj) modalValue.value = props.activeCategoryObj[fieldType]
      else {
        modalValue.value = null
        $q.notify({
            color: 'orange-6',
            message: `Selected Category Has no ${fieldType.replaceAll('_', ' ')} !`,
            icon: 'report_problem',
            position: 'top-right',
        })
      }
    } else modalValue.value = null
  }
  else if (newValue === 'global') {
    modalValue.value = globalAccountObjComputed.value.id
  }
  else {
    modalValue.value = null
  }
}
watch(
    () => props.modelValue,
    (newValue) => {
        modalValue.value = newValue
    }
)
watch(
    () => props.typeModelValue,
    (newValue) => {
        type.value = newValue
    }
)
watch(
    () => type.value, (newValue) => emits('update:typeModelValue', newValue)
)
watch(
    () => modalValue.value, (newValue) => emits('update:modelValue', newValue)
)
const globalAccountName = {
    'Sales': 'Sales Account',
    'Purchase': 'Purchase Account',
    'Discount Allowed': 'Discount Expenses',
    'Discount Received': 'Discount Income'
}
const globalAcIdKeyMap = {
    'Sales': 'sales_account_id',
    'Purchase': 'purchase_account_id',
    'Discount Allowed': 'discount_allowed_account_id',
    'Discount Received': 'discount_received_account_id'
}
const globalAccountObjComputed = computed(() => {
    const data = {
        id: null,
        name: null
    }
    if (!props.globalAccounts) return data
    if (props.globalAccounts.hasOwnProperty(globalAcIdKeyMap[props.label])) {
        data.id = props.globalAccounts[globalAcIdKeyMap[props.label]]
        data.name = globalAccountName[props.label]
    }
    return data
})
const dedicatedAccountName = computed(() => {
  if (props.label === 'Sales') return (props.itemName + ' (Sales)')
  else if (props.label === 'Purchase') return (props.itemName + ' (Purchase)')
  else if (props.label === 'Discount Allowed') return ('Discount Allowed - ' + props.itemName)
  else if (props.label === 'Discount Received') return ('Discount Received - ' + props.itemName)
  else return ''
})
const categoryAccountNameComputed = computed(() => {
  let categoryName = null
  if (props.activeCategoryObj && props.activeCategory) {
    categoryName = props.activeCategoryObj.name
  }
  else if (props.activeCategory && props.defaultCategoryName) {
    categoryName = props.defaultCategoryName
  }
  if (!categoryName) return null
  if (props.label === 'Sales') return (categoryName + ' (Sales)')
  else if (props.label === 'Purchase') return (categoryName + ' (Purchase)')
  else if (props.label === 'Discount Allowed') return ('Discount Allowed - ' + categoryName)
  else if (props.label === 'Discount Received') return ('Discount Received - ' + categoryName)
  return null
})
const endpointLabelMap = {
  'Sales': 'v1/items/create-defaults/accounts',
  'Purchase': 'v1/items/create-defaults/accounts',
  'Discount Allowed': 'v1/items/create-defaults/discount_allowed_accounts',
  'Discount Received': 'v1/items/create-defaults/discount_received_accounts'
}
</script>
