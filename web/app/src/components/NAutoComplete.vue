<template>
  <div class="row no-wrap">
    <q-select :autofocus="focusOnMount" v-model="modalValue" input-debounce="0" :label="label" use-input :options="filteredOptions" @filter="filterFn" :option-value="optionValue" option-label="name" map-options emit-value class="q-mr-xs col" @update:modelValue="valUpdated" :disable="props.disabled" :error-message="props?.error" :error="!!props?.error" clearable clear-icon="close">
      <template #no-option>
        <div class="py-3 px-4 bg-slate-1">No Results Found</div>
      </template>
    </q-select>
    <div>
      <q-btn v-if="modalComponent" color="white" label="+" class="q-ml-auto text-black q-mt-md" @click="openModal" />
    </div>
  </div>
  <q-dialog v-model="isModalOpen" transition-hide="none">
    <q-card style="min-width: 80vw">
      <q-btn style="position: absolute; right: 8px; top: 8px; z-index: 50" push color="red" text-color="white" round dense icon="close" @click="closeModal" />
      <div
        :class="
          modalFormLoading.hasOwnProperty(`${modalId}`) ?
            modalFormLoading[modalId] ?
              ''
            : 'hidden'
          : ''
        "
      >
        <component :is="FormSkeleton"></component>
      </div>
      <div
        :class="
          modalFormLoading.hasOwnProperty(`${modalId}`) ?
            modalFormLoading[modalId] ?
              'hidden'
            : ''
          : 'hidden'
        "
      >
        <component :is="modalComponent" :is-modal="true" @modalSignal="handleModalSignal" @closeModal="closeModal" @getModalId="(id) => (modalId = id)"></component>
      </div>
    </q-card>
  </q-dialog>
</template>

<script>
// import { useLoginStore } from 'src/stores/login-info'
import FormSkeleton from './FormSkeleton.vue'
import { useModalFormLoading } from 'src/stores/ModalFormLoading'
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
        filteredOptions.value = allOptions.value.filter((v) => v.name.toLowerCase().indexOf(needle) > -1)
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
