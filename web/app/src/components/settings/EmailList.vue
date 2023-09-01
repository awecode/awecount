<template>
    <div>
        <div class="row" v-for="(value, index) in modelValue" :key="index">
            <div class="col-12 col-md-6 row items-end q-gutter-md">
                <q-input v-model="propsModelValue[index]" type="email" label="Email" style="flex-grow: 1;" :error="!!(props.errors && props.errors[index])" :error-message="(props.errors && props.errors[index]) ? props.errors[index][0] : null"></q-input>
                <q-btn @click="removeEmail(index)" style="flex-grow: 0; flex-shrink: 0;" icon="delete" size="md" color="red-5" title="Remove Email"></q-btn>
            </div>
        </div>
        <q-btn @click="addEmail" color="green" outline class="q-px-lg q-py-ms q-mt-lg">Add Email</q-btn>
    </div>
</template>

<script setup>
    const props = defineProps({
        modelValue : {
            type: Array,
            default: () => []
        },
        errors : {
            type: Object,
            default: () => ({})
        }
    })
    const propsModelValue = ref(props.modelValue)
    watch(propsModelValue, (newVal) => {
        debugger
        emit('update:modelValue', newVal)
    })
    const addEmail = () => {
        propsModelValue.value.push('')
    }
    const removeEmail = (index) => {
        propsModelValue.value.splice(index, 1)
    }
    onMounted(() => {
        if (propsModelValue.value && propsModelValue.value.length === 0) addEmail()
    })
</script>