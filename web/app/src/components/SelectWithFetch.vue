<template>
  <div class="row no-wrap">
    <q-select
      v-model="modalValue"
      input-debounce="0"
      :label="label"
      use-input
      :options="options"
      @filter="filterFn"
      option-value="id"
      option-label="name"
      map-options
      emit-value
      class="q-mr-xs col"
      @update:modelValue="valUpdated"
      :disable="props.disabled"
      :error-message="props?.error"
      :error="!!props?.error"
    />
    <div>
      <q-btn
        v-if="modalComponent"
        color="white"
        label="+"
        class="q-ml-auto text-black q-mt-md"
        @click="openModal"
      />
    </div>
  </div>
</template>

<script setup>
const props = defineProps[('label', 'modelValue', 'endpoint', 'error')]
const options = await useApi(endpoint, { method: 'GET' })
  .then((data) => {
    this.options = data
  })
  .catch((error) => {
    console.log('Error Fetching options Due To', error)
  })

// export default {
//   props: {
//     label: {
//       type: String,
//       default: 'Select',
//     },
//     modelValue: {
//       type: [Object, String, Number],
//       default: () => null,
//     },
//     endpoint: {
//       type: [String, null],
//       default: () => null,
//     },
//     error: {
//       type: String,
//       required: false,
//     },
//   },
//   emits: ['update:modelValue'],

//   setup(props, { emit }) {
//     const options = ref([])
//     const valUpdated = (val) => {
//       emit('update:modelValue', val)
//     }
//     const modalValue = ref(props.modelValue)

//     watch(
//       () => props.modelValue,
//       (newValue) => {
//         modalValue.value = newValue
//       }
//     )

//     return {
//       valUpdated,
//       props,
//       modalValue,
//       options,
//     }
//   },
//   mounted() {
//     console.log('mounted', props.endpoint)
//     const endpoint = props.endpoint
//     useApi(endpoint, { method: 'GET' })
//       .then((data) => {
//         this.options = data
//       })
//       .catch((error) => {
//         console.log('Error Fetching options Due To', error)
//       })
//   },
// }
</script>
