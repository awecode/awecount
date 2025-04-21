<script>
export default defineNuxtComponent({
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
})
</script>

<template>
  <h6 v-if="modalValue && modalValue.length > 0" class="q-mt-lg q-mb-md">
    Contact Person
  </h6>
  <q-card v-for="(representative, index) in modalValue" :key="index" class="q-pa-md q-mb-md">
    <div class="flex flex-col gap-y-4">
      <div class="row q-col-gutter-md">
        <q-input
          v-model="representative.name"
          class="col-12 col-md-6"
          label="Name"
          :error="rowErrorComp"
          @change="updateVal"
        />
        <q-input
          v-model="representative.position"
          class="col-12 col-md-6"
          label="Positions"
          @change="updateVal"
        />
      </div>
      <div class="row q-col-gutter-md">
        <q-input
          v-model="representative.phone"
          class="col-12 col-md-6"
          label="Phone Number"
          type="number"
          @change="updateVal"
        />
        <q-input
          v-model="representative.email"
          class="col-12 col-md-6"
          label="Email"
          type="email"
          :error="!!errors[index]?.email"
          :error-message="!!errors[index]?.email ? errors[index]?.email[0] : ''"
          @change="updateVal"
        />
      </div>
    </div>
  </q-card>
</template>
