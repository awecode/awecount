<template>
    <div class="grid grid-cols-2 gap-4">
        <div>
            <q-select class="q-full-width" :label="`${label} A/C Options`" option-value="value" option-label="label"
                map-options emit-value v-model="type" :options="account_types" :error="false"/>
        </div>
        <div>
            <n-auto-complete v-if="type === 'existing'" class="q-full-width" :label="`${label} Account`"
                v-model="modalValue" :options="props.options"
                :modal-component="checkPermissions('AccountCreate') ? LedgerForm : null" :error="error" />
            <div v-else-if="type === 'dedicated'" class="h-full w-full items-center" style="display: flex; gap: 10px;">
                <div v-if="dedicatedAccount && !usedInCategoryForm" class="w-full">
                  <q-input :label="label + ' Account'" class="w-full" disable :error="false" v-model="dedicatedAccountName"></q-input>
                </div>
                <div v-else class="flex gap-2 items-center">
                  <q-icon name="info" size="sm" color="grey-7"></q-icon>
                  <div class="text-grey-7">A new {{ props.label }} Account will be created for the Item</div>
                </div>
                <!-- {{ props.itemName ? `${props.itemName || ''} (${label})` : '' }} -->
            </div>
            <div v-else-if="type === 'category'" class="flex items-center h-full">
              <div v-if="usedInCategoryForm" class="flex gap-2 items-end">
                <q-icon name="info" size="sm" color="grey-7"></q-icon>
                <div class="text-grey-7">Category's {{ props.label }} Account will be used for the Item</div>
              </div>
              <div v-else class="w-full">
                <q-select :label="`${label} Account`" option-value="id" option-label="name" map-options emit-value
                v-model="modalValue" disable :options="props.options" :error="!!error" :error-message="error"></q-select>
              </div>
            </div>
            <div v-else-if="type === 'creation' && usedInCategoryForm" class="flex items-center gap-2 h-full">
              <q-icon name="info" size="sm" color="grey-7"></q-icon>
              <div class="text-grey-7">You will be able to choose options while creating item.</div>
            </div>
            <q-select v-else :label="`${label} Account`" option-value="id" option-label="name" map-options emit-value
                v-model="modalValue" disable :options="props.options" :error="!!error" :error-message="error"></q-select>
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
        type: Array,
        default: () => []
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
    inventory_categories: {
        type: Array,
        default: () => []
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
      type: Number || null,
      default: () => null
    }
})
const $q = useQuasar()
const emits = defineEmits(['update:modelValue', 'update:typeModelValue'])
const type = ref(props.typeModelValue)
const modalValue = ref(props.modelValue)
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
watch(() => type.value, (newValue) => {
    if (newValue === 'category') {
        if (props.activeCategory && !props.usedInCategoryForm) {
            const selected = props.inventory_categories.find(item => {
                if (item.id === props.activeCategory) {
                    return item;
                }
            })
            const fieldType = props.label.toLowerCase().replaceAll(' ', '_') + '_account'
            if (selected) modalValue.value = selected[fieldType]
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
        modalValue.value = getOptionCollection(props.options, globalAccountName[props.label])
    }
    else {
        modalValue.value = null
    }
})
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
const dedicatedAccountName = computed(() => {
  if (props.label === 'Sales') return (props.itemName + ' (Sales)')
  else if (props.label === 'Purchase') return (props.itemName + ' (Purchase)')
  else if (props.label === 'Discount Allowed') return ('Discount Allowed - ' + props.itemName)
  else if (props.label === 'Discount Received') return ('Discount Received - ' + props.itemName)
  else return ''
})
</script>
