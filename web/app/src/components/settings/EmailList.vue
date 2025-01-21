<script setup>
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  errors: {
    type: Object,
    default: () => ({}),
  },
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

<template>
  <div>
    <div v-for="(value, index) in modelValue" :key="index" class="row">
      <div class="col-12 col-md-6 row items-center q-gutter-md">
        <q-input
          v-model="propsModelValue[index]"
          label="Email"
          style="flex-grow: 1"
          type="email"
          :error="!!(props.errors && props.errors[index])"
          :error-message="props.errors && props.errors[index] ? props.errors[index][0] : null"
        />
        <q-btn
          color="red-5"
          icon="delete"
          size="md"
          style="flex-grow: 0; flex-shrink: 0"
          @click="removeEmail(index)"
        >
          <q-tooltip>Remove Email</q-tooltip>
        </q-btn>
      </div>
    </div>
    <q-btn
      outline
      class="q-px-lg q-py-ms q-mt-lg"
      color="green"
      @click="addEmail"
    >
      Add Email
    </q-btn>
  </div>
</template>
