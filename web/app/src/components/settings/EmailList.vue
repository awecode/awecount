<template>
  <div>
    <div class="row" v-for="(value, index) in modelValue" :key="index">
      <div class="col-12 col-md-6 row items-center q-gutter-md">
        <q-input v-model="propsModelValue[index]" type="email" label="Email" style="flex-grow: 1;"
          :error="!!(props.errors && props.errors[index])"
          :error-message="(props.errors && props.errors[index]) ? props.errors[index][0] : null"></q-input>
        <q-btn @click="removeEmail(index)" style="flex-grow: 0; flex-shrink: 0;" icon="delete" size="md" color="red-5">
          <q-tooltip>Remove Email</q-tooltip>
        </q-btn>
      </div>
    </div>
    <q-btn @click="addEmail" color="green" outline class="q-px-lg q-py-ms q-mt-lg">Add Email</q-btn>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  errors: {
    type: Object,
    default: () => ({})
  }
})
const emit = defineEmits(['updateErrors'])
const propsModelValue = ref(props.modelValue)
watch(propsModelValue, (newVal) => {
  emit('update:modelValue', newVal)
})
const addEmail = () => {
  propsModelValue.value.push('')
}
const removeEmail = (index) => {
  propsModelValue.value.splice(index, 1)
  emit('updateErrors')
}
onMounted(() => {
  if (propsModelValue.value && propsModelValue.value.length === 0) addEmail()
})
</script>
