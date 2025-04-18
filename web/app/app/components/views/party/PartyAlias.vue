<script>
export default {
  props: {
    modelValue: {
      type: Array,
      default: () => [],
    },
    errors: {
      type: [Object, String],
      default: () => {
        return {}
      },
    },
    index: {
      type: Number,
      default: 0,
    },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const modalValue = ref(props.modelValue)
    const updateVal = () => {
      emit('update:modelValue', modalValue.value)
    }
    const rowErrorComp = computed(() => {
      if (typeof props.errors === 'string') return true
      else return false
    })
    watch(
      () => props.modelValue,
      newValue => (modalValue.value = newValue),
    )
    return {
      modalValue,
      updateVal,
      rowErrorComp,
    }
  },
}
</script>

<template>
  <h6 v-if="modalValue && modalValue.length > 0" class="q-mt-lg q-mb-md">
    Aliases
  </h6>
  <q-card v-for="(alias, index) in modalValue" :key="index" class="q-pa-md q-mb-md">
    <div class="flex flex-col gap-y-4">
      <div class="row q-col-gutter-md">
        <q-input
          v-model="modalValue[index]"
          class="col-12 col-md-6"
          label="Name"
          :error="rowErrorComp"
          @change="updateVal"
        />
      </div>
    </div>
  </q-card>
</template>
