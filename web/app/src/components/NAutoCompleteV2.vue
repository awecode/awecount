<script setup lang="ts">
import useApi from 'src/composables/useApi'
import { withQuery } from 'ufo'
import { ref, watch } from 'vue'

interface Props {
  label?: string
  modelValue?: any
  options?: {
    results: any[]
    pagination: Record<string, any>
  }
  modalComponent?: any
  disabled?: boolean
  error?: string
  focusOnMount?: boolean
  endpoint?: string | null
  staticOption?: any
  emitObj?: boolean
  fetchOnMount?: boolean
  dataTestid?: string
  mapOptions?: boolean
  errorMessage?: string
  optionValue?: string
  emitValue?: boolean
  optionLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  label: 'Select',
  modelValue: null,
  options: () => ({ results: [], pagination: {} }),
  modalComponent: undefined,
  disabled: false,
  error: undefined,
  focusOnMount: false,
  endpoint: null,
  staticOption: undefined,
  emitObj: false,
  fetchOnMount: false,
  dataTestid: undefined,
  mapOptions: false,
  errorMessage: undefined,
  optionValue: undefined,
  emitValue: false,
  optionLabel: undefined,
})

const emit = defineEmits<{
  'update:modelValue': [value: any]
  'updateObj': [value: any]
}>()

const modalValue = ref(props.modelValue)
const initalAllOptions = props.options
if (props.staticOption?.id) {
  initalAllOptions.results = initalAllOptions.results.filter((item) => {
    return props.staticOption.id !== item.id
  })
  initalAllOptions.results.unshift(props.staticOption)
}
const allOptions = ref(initalAllOptions)
const isModalOpen = ref(false)
const filteredOptions = ref(allOptions.value.results || [])
const fetchLoading = ref(false)
const filteredOptionsPagination = ref(null)
const serachKeyword = ref(null)

const valUpdated = (val: any) => {
  emit('update:modelValue', val)
}

watch(
  () => props.modelValue,
  (newValue) => {
    modalValue.value = newValue
    if (props.emitObj) {
      let data = null
      if (filteredOptions.value?.length) {
        const index = filteredOptions.value.findIndex((item) => {
          return item.id === newValue
        })
        if (index > -1) {
          data = filteredOptions.value[index]
        }
      }
      emit('updateObj', data)
    }
  },
)

watch(
  () => props.options,
  (newValue) => {
    if (!newValue) return
    if (props.staticOption?.id) {
      const cleanedOptions = newValue.results.filter((item) => {
        return props.staticOption.id !== item.id
      })
      cleanedOptions.unshift(props.staticOption)
      allOptions.value.results = cleanedOptions
      filteredOptions.value = cleanedOptions
    } else {
      allOptions.value.results = newValue.results
      filteredOptions.value = newValue.results
    }
    Object.assign(allOptions.value.pagination, newValue.pagination)
  },
)

watch(
  () => props.staticOption,
  (newValue) => {
    if (newValue?.id) {
      const cleanedOptions = allOptions.value.results.filter((item) => {
        return newValue.id !== item.id
      })
      cleanedOptions.unshift(newValue)
      allOptions.value.results = cleanedOptions
      filteredOptions.value = cleanedOptions
    }
  },
)

const filterFn = async (val: string, update: (callback: () => void) => void) => {
  serachKeyword.value = val
  if (val === '') {
    update(() => {
      filteredOptions.value = allOptions.value.results
      filteredOptionsPagination.value = null
    })
    return
  }
  update(async () => {
    try {
      const endpoint = `${props.endpoint}?search=${val}`
      const data = await useApi(endpoint)
      filteredOptions.value = data.results
      filteredOptionsPagination.value = data.pagination
    } catch (err) {
      console.error(`Error While Fetching ${err}`)
    }
  })
}

const openModal = () => {
  isModalOpen.value = true
}

const handleModalSignal = (v: any) => {
  allOptions.value.results.push(v)
  isModalOpen.value = false
  emit('update:modelValue', v.id)
}

const closeModal = () => {
  isModalOpen.value = false
}

const fetchOptions = async () => {
  fetchLoading.value = true
  const queryObj: Record<string, any> = {}
  if (allOptions.value?.pagination?.page) queryObj.page = allOptions.value.pagination.page + 1
  if (props.fetchOnMount && modalValue.value) queryObj.id = modalValue.value
  const endpoint = withQuery(props.endpoint || '', queryObj)
  try {
    const data = await useApi(endpoint)
    if (data) {
      if (props.staticOption?.id) {
        const filteredOptions = data.results.filter((item) => {
          return props.staticOption.id !== item.id
        })
        allOptions.value.results.push(...filteredOptions)
      } else {
        allOptions.value.results.push(...data.results)
      }
      Object.assign(allOptions.value.pagination, data.pagination)
    }
    fetchLoading.value = false
  } catch (error) {
    console.error('Error While Fetching Options', error)
    fetchLoading.value = false
  }
}

const onScroll = async (scrollData: { direction: string, to: number }) => {
  if (filteredOptionsPagination.value) {
    if (
      scrollData.direction === 'increase'
      && scrollData.to > filteredOptions.value.length - 2
      && !(filteredOptionsPagination.value.page >= filteredOptionsPagination.value.pages)
      && !fetchLoading.value
    ) {
      fetchLoading.value = true
      try {
        const endpoint = `${props.endpoint}?search=${serachKeyword.value}&page=${filteredOptionsPagination.value.page + 1}`
        const data = await useApi(endpoint)
        filteredOptions.value.push(...data.results)
        filteredOptionsPagination.value = data.pagination
      } catch (err) {
        console.error(`Error While Fetching ${err}`)
      } finally {
        fetchLoading.value = false
      }
    }
  } else if (
    scrollData.direction === 'increase'
    && scrollData.to > allOptions.value.results.length - 3
    && allOptions.value.pagination.page !== allOptions.value.pagination.pages
    && !fetchLoading.value
  ) {
    await fetchOptions()
  }
}

if (props.fetchOnMount && props.endpoint) {
  fetchOptions()
}
</script>

<template>
  <div class="row no-wrap" v-bind="$attrs">
    <q-select
      v-model="modalValue"
      clearable
      emit-value
      map-options
      use-input
      class="q-mr-xs col"
      clear-icon="close"
      option-label="name"
      option-value="id"
      :autofocus="focusOnMount"
      :disable="disabled"
      :error="!!error"
      :error-message="error"
      :label="label"
      :loading="fetchLoading"
      :options="filteredOptions"
      :virtual-scroll-slice-ratio-after="0"
      @filter="filterFn"
      @update:model-value="valUpdated"
      @virtual-scroll="onScroll"
    >
      <template #no-option>
        <div class="py-3 px-4 bg-slate-1">
          No Results Found
        </div>
      </template>
      <template v-if="fetchLoading" #after-options>
        <div class="flex justify-center pb-2 text-gray-500">
          <svg
            height="32"
            viewBox="0 0 24 24"
            width="32"
            xmlns="http://www.w3.org/2000/svg"
          >
            <g
              fill="none"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-width="2"
            >
              <path
                d="M12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3Z"
                stroke-dasharray="60"
                stroke-dashoffset="60"
                stroke-opacity=".3"
              >
                <animate
                  attributeName="stroke-dashoffset"
                  dur="1.3s"
                  fill="freeze"
                  values="60;0"
                />
              </path>
              <path d="M12 3C16.9706 3 21 7.02944 21 12" stroke-dasharray="15" stroke-dashoffset="15">
                <animate
                  attributeName="stroke-dashoffset"
                  dur="0.3s"
                  fill="freeze"
                  values="15;0"
                />
                <animateTransform
                  attributeName="transform"
                  dur="1.5s"
                  repeatCount="indefinite"
                  type="rotate"
                  values="0 12 12;360 12 12"
                />
              </path>
            </g>
          </svg>
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
      <component
        :is="modalComponent"
        :is-modal="true"
        @close-modal="closeModal"
        @modal-signal="handleModalSignal"
      />
    </q-card>
  </q-dialog>
</template>
