<template>
  <h6 class="q-mt-lg q-mb-md" v-if="modalValue && modalValue.length > 0">Contact Person</h6>
  <q-card
    v-for="(representative, index) in modalValue"
    :key="index"
    class="q-pa-md q-mb-md"
  >
    <div>
      <div class="row q-col-gutter-md">
        <q-input
          v-model="representative.name"
          label="Name"
          class="col-12 col-md-6"
          :error="rowErrorComp"
          @change="updateVal"
        />
        <q-input
          v-model="representative.position"
          label="Positions"
          class="col-12 col-md-6"
          @change="updateVal"
        />
      </div>
      <div class="row q-col-gutter-md">
        <q-input
          v-model="representative.phone"
          label="Phone Number"
          class="col-12 col-md-6"
          @change="updateVal"
          type="number"
        />
        <q-input
          v-model="representative.email"
          label="Email"
          class="col-12 col-md-6"
          type="email"
          @change="updateVal"
          :error="!!errors[index]?.email"
          :error-message="!!errors[index]?.email ? errors[index]?.email[0] : ''"
        />
      </div>
    </div>
  </q-card>
</template>
<script>
export default {
  props: {
    modelValue: {
      type: Array,
      default: () => [
        {
          name: null,
          position: null,
          phone: null,
          email: null,
        },
      ],
    },
    errors: {
      type: [Object, String],
      default: () => {
        return {}
      },
    },
    index:{
      type: Number,
      default: 0
    }
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
      (newValue) => (modalValue.value = newValue)
    )
    return {
      modalValue,
      updateVal,
      rowErrorComp,
    }
  },
}
</script>
