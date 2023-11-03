<template>
    <div class="grid grid-cols-2 gap-4">
        <div>
            <q-select class="q-full-width" :label="`${label} A/C Options`" option-value="value" option-label="label"
                map-options emit-value v-model="type" :options="account_types" :error="false"/>
        </div>
        <div>
            <n-auto-complete v-if="type === 'existing'" class="q-full-width" :label="`${label} Account`"
                v-model="modalValue" :options="props.options"
                :modal-component="checkPermissions('AccountCreate') ? AccountForm : null" :error="error" />
            <div v-else-if="type === 'dedicated'" class="h-full w-full items-center" style="display: flex; gap: 10px;">
                <q-icon name="info" size="sm" color="grey-7"></q-icon>
                <div class="text-grey-7">A new {{ props.label }} Account will be created for the Item</div>
                <!-- {{ props.itemName ? `${props.itemName || ''} (${label})` : '' }} -->
            </div>
            <q-select v-else :label="`${label} Account`" option-value="id" option-label="name" map-options emit-value
                v-model="modalValue" disable :options="props.options" :error="!!error" :error-message="error"></q-select>
        </div>
    </div>
</template>

<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import AccountForm from 'src/pages/bank/account/AccountForm.vue'
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
    }
})
const emits = defineEmits(['update:modelValue', 'update:typeModelValue'])
const type = ref(props.typeModelValue)
const modalValue = ref(props.modelValue)
// const options
const account_types = props.usedInCategoryForm ? [
    { value: 'create', label: 'Create New Account' },
    { value: 'dedicated', label: 'Use an Existing Account' },
    { value: 'global', label: 'Use Global Account' },
] : [
    { value: 'global', label: 'Use Global Account' },
    { value: 'category', label: "Use Category's Account" },
    { value: 'dedicated', label: 'Use a Dedicated Account' },
    { value: 'existing', label: 'Use an Existing Account' },
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
    if (newValue === "category") {
        if (props.activeCategory) {
            const selected = props.inventory_categories.find(item => {
                if (item.id === props.activeCategory) {
                    return item;
                }
            })
            const fieldType = props.label.toLowerCase().replaceAll(' ', '_') + '_account'
            if (selected) modalValue.value = selected[fieldType]
            else modalValue.value = null
        } else modalValue.value = null
    }
    else if (newValue === "global") {
        // const globalAccountName = props.label
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
</script>
