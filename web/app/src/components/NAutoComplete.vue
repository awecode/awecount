<template>
  <div class="row no-wrap">
    <q-select
      :model-value="modelValue"
      input-debounce="0"
      :label="label"
      use-input
      :options="filteredOptions"
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
  <q-dialog v-model="isModalOpen">
    <q-card style="min-width: 80vw">
      <component
        :is="modalComponent"
        :is-modal="true"
        @modalSignal="handleModalSignal"
        @closeModal="closeModal"
      >
      </component>
    </q-card>
  </q-dialog>
</template>

<script>
export default {
  props: {
    label: {
      type: String,
      default: 'Select',
    },
    modelValue: {
      type: [Object, String, Number],
      default: () => null,
    },
    options: {
      type: Array,
      default: () => [],
    },
    modalComponent: {
      type: Object,
      required: false,
    },
    disabled: {
      type: Boolean,
      required: false,
      default: () => false,
    },
    error: {
      type: String,
      required: false,
    },
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const valUpdated = (val) => {
      emit('update:modelValue', val);
    };

    const allOptions = ref(props.options || []);
    const isModalOpen = ref(false);
    const filteredOptions = ref(props.options);

    watch(
      () => props.options,
      (newValue) => {
        allOptions.value = newValue;
        filteredOptions.value = newValue;
      }
    );

    const filterFn = (val, update) => {
      if (val === '') {
        update(() => {
          filteredOptions.value = allOptions.value;
        });
        return;
      }
      update(() => {
        const needle = val.toLowerCase();
        filteredOptions.value = allOptions.value.filter(
          (v) => v.name.toLowerCase().indexOf(needle) > -1
        );
      });
    };

    const openModal = () => {
      isModalOpen.value = true;
    };

    const handleModalSignal = (v) => {
      allOptions.value.push(v);
      isModalOpen.value = false;
      emit('update:modelValue', v.id);
    };

    const closeModal = () => {
      isModalOpen.value = false;
    };

    return {
      filteredOptions,
      filterFn,
      valUpdated,
      isModalOpen,
      openModal,
      closeModal,
      handleModalSignal,
      props,
    };
  },
};
</script>
