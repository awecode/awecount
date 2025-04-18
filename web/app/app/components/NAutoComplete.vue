<script>
import { useModalFormLoading } from '@/stores/ModalFormLoading'
// import { useLoginStore } from '@/stores/login-info'
import FormSkeleton from './FormSkeleton.vue'

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
    focusOnMount: {
      type: Boolean,
      default: false,
    },
    optionValue: {
      type: String,
      default: 'id',
    },
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const modalFormLoading = useModalFormLoading()
    const valUpdated = (val) => {
      emit('update:modelValue', val)
    }
    const modalValue = ref(props.modelValue)
    const allOptions = ref(props.options || [])
    const isModalOpen = ref(false)
    const filteredOptions = ref(props.options)

    watch(
      () => props.modelValue,
      (newValue) => {
        modalValue.value = newValue
      },
    )

    watch(
      () => props.options,
      (newValue) => {
        allOptions.value = newValue
        filteredOptions.value = newValue
      },
    )

    const filterFn = (val, update) => {
      if (val === '') {
        update(() => {
          filteredOptions.value = allOptions.value
        })
        return
      }
      update(() => {
        const needle = val.toLowerCase()
        filteredOptions.value = allOptions.value.filter(v => v.name.toLowerCase().includes(needle))
      })
    }

    const openModal = () => {
      isModalOpen.value = true
    }

    const handleModalSignal = (v) => {
      allOptions.value.push(v)
      isModalOpen.value = false
      emit('update:modelValue', v.id)
    }

    const closeModal = () => {
      isModalOpen.value = false
    }
    const modalId = ref(null)
    return {
      filteredOptions,
      filterFn,
      valUpdated,
      isModalOpen,
      openModal,
      closeModal,
      handleModalSignal,
      props,
      modalValue,
      FormSkeleton,
      modalFormLoading,
      modalId,
    }
  },
}
</script>

<template>
  <div class="row no-wrap">
    <q-select
      v-model="modalValue"
      clearable
      emit-value
      map-options
      use-input
      class="q-mr-xs col"
      clear-icon="close"
      input-debounce="0"
      option-label="name"
      :autofocus="focusOnMount"
      :disable="props.disabled"
      :error="!!props?.error"
      :error-message="props?.error"
      :label="label"
      :option-value="optionValue"
      :options="filteredOptions"
      @filter="filterFn"
      @update:model-value="valUpdated"
    >
      <template #no-option>
        <div class="py-3 px-4 bg-slate-1">
          No Results Found
        </div>
      </template>
    </q-select>
    <div>
      <q-btn
        v-if="modalComponent"
        class="q-ml-auto text-black q-mt-md"
        color="white"
        label="+"
        @click="openModal"
      />
    </div>
  </div>
  <q-dialog v-model="isModalOpen" transition-hide="none">
    <q-card style="min-width: 80vw">
      <q-btn
        dense
        push
        round
        color="red"
        icon="close"
        style="position: absolute; right: 8px; top: 8px; z-index: 50"
        text-color="white"
        @click="closeModal"
      />
      <!-- {{ modalId }}
      {{ modalFormLoading }}
      <div
        :class="
          modalFormLoading.hasOwnProperty(`${modalId}`)
            ? modalFormLoading[modalId]
              ? ''
              : 'hidden'
            : ''
        "
      >
        <component :is="FormSkeleton" />
      </div> -->
      <div>
        <component
          :is="modalComponent"
          :is-modal="true"
          @close-modal="closeModal"
          @get-modal-id="(id) => {
            modalId = id
          }"
          @modal-signal="handleModalSignal"
        />
      </div>
    </q-card>
  </q-dialog>
</template>
