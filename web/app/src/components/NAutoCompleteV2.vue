<template>
  <div class="row no-wrap">
    <q-select :autofocus="focusOnMount" v-model="modalValue" input-debounce="0" :label="label" use-input
      :options="filteredOptions" option-value="id" option-label="name" map-options emit-value
      class="q-mr-xs col" @update:modelValue="valUpdated" :disable="props.disabled" :error-message="props?.error"
      :error="!!props?.error" clearable clear-icon="close" @virtual-scroll="onScroll">
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
      <component :is="modalComponent" :is-modal="true" @modalSignal="handleModalSignal" @closeModal="closeModal">
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
      type: Object,
      default: () => { return {
          results: [],
          pagination: {}
        }
      }
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
      default: false
    },
    endpoint: {
      type: [String, null],
      default: () => null
    }
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const valUpdated = (val) => {
      emit('update:modelValue', val)
    }
    const modalValue = ref(props.modelValue)
    const allOptions = ref(props.options.results)
    const isModalOpen = ref(false)
    const filteredOptions = ref(props?.options?.results || [])
    const fetchLoading = ref(false)

    watch(
      () => props.modelValue,
      (newValue) => {
        modalValue.value = newValue
      }
    )

    watch(
      () => props.options,
      (newValue) => {
        allOptions.value = newValue
        filteredOptions.value = newValue.results
      }
    )

    const filterFn = (val, update) => {
      if (val === '') {
        update(() => {
          filteredOptions.value = allOptions.value.results
        })
        return
      }
      update(() => {
        const needle = val.toLowerCase()
        filteredOptions.value = allOptions.value.results.filter(
          (v) => v.name.toLowerCase().indexOf(needle) > -1
        )
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
    const fetchOptions = () => {
        fetchLoading.value = true
        const endpoint = props.endpoint + (allOptions.value?.pagination?.page ? `?page=${allOptions.value.pagination.page + 1}` : '')
        useApi(endpoint).then((data) => {
          allOptions.value.results.push(...data.results)
          Object.assign(allOptions.value.pagination, data.pagination)
          fetchLoading.value = false
        }).catch((err) => {
          console.log('Error While Fetching Options', err)
          fetchLoading.value = false
        })
    }
    if (props.endpoint) fetchOptions()
    const onScroll = (scrollData) => {
      if (scrollData.direction === "increase" && scrollData.to > allOptions.value.results.length - 3 &&
          allOptions.value.pagination.page !== allOptions.value.pagination.pages && !fetchLoading.value) {
        fetchOptions()
      }
    }

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
      onScroll
    }
  },
}
</script>
