<script setup>
import useApi from '@/composables/useApi'
import { ref, watch } from 'vue'

const props = defineProps(['modelValue', 'endpoint', 'label'])
const emit = defineEmits(['update:modelValue'])
const options = ref([])
const modalValue = ref(props.modelValue)
useApi(props.endpoint, { method: 'GET' })
  .then((data) => {
    options.value = data
  })
  .catch((error) => {
    console.log('Error Fetching options Due To', error)
  })
watch(
  () => props.modelValue,
  newValue => (modalValue.value = newValue),
)
const valUpdated = (val) => {
  emit('update:modelValue', val)
}
</script>

<template>
  <div class="row no-wrap">
    <q-select
      v-model="modalValue"
      dense
      emit-value
      map-options
      use-input
      class="col"
      input-debounce="0"
      option-label="name"
      option-value="id"
      :disable="props?.disabled"
      :error="!!props?.error"
      :error-message="props?.error"
      :label="props.label"
      :options="options"
      @update:model-value="valUpdated"
    />
  </div>
</template>
