<template>
  <div class="row no-wrap">
    <q-select
      v-model="modalValue"
      input-debounce="0"
      :label="props.label"
      use-input
      :options="options"
      option-value="id"
      option-label="name"
      map-options
      emit-value
      class="col"
      @update:modelValue="valUpdated"
      :disable="props?.disabled"
      :error-message="props?.error"
      :error="!!props?.error"
      dense
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import useApi from 'src/composables/useApi'
const options = ref([])
const props = defineProps(['modelValue', 'endpoint', 'label'])
const emit = defineEmits(['update:modelValue'])
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
  (newValue) => (modalValue.value = newValue)
)
const valUpdated = (val) => {
  emit('update:modelValue', val)
}
</script>
