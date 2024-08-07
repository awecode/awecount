<template>
  <div class="row no-wrap">
    <q-select :loading="fetchLoading" :autofocus="focusOnMount" v-model="modalValue" :label="label" use-input
      :options="filteredOptions" option-value="id" option-label="name" map-options emit-value class="q-mr-xs col"
      @update:modelValue="valUpdated" :disable="props.disabled" :error-message="props?.error" :error="!!props?.error"
      clearable clear-icon="close" @virtual-scroll="onScroll" @filter="filterFn"
      virtual-scroll-slice-ratio-after="-0.05" @popup-show="isActive = true" @popup-hide="() => isActive = false">
      <template #no-option>
        <div class="py-3 px-4 bg-slate-1">No Results Found</div>
      </template>
      <template v-if="fetchLoading" #after-options>
        <div class="flex justify-center pb-2 text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24">
            <g fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="2">
              <path stroke-dasharray="60" stroke-dashoffset="60" stroke-opacity=".3"
                d="M12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3Z">
                <animate fill="freeze" attributeName="stroke-dashoffset" dur="1.3s" values="60;0" />
              </path>
              <path stroke-dasharray="15" stroke-dashoffset="15" d="M12 3C16.9706 3 21 7.02944 21 12">
                <animate fill="freeze" attributeName="stroke-dashoffset" dur="0.3s" values="15;0" />
                <animateTransform attributeName="transform" dur="1.5s" repeatCount="indefinite" type="rotate"
                  values="0 12 12;360 12 12" />
              </path>
            </g>
          </svg>
        </div>
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
import { withQuery, joinURL } from 'ufo'
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
      default: () => {
        return {
          results: [],
          pagination: {},
        }
      },
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
    },
    staticOption: {
      type: [Object, undefined],
      required: false
    },
    emitObj: {
      type: Boolean,
      default: false
    },
    fetchOnMount: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'updateObj'],

  setup(props, { emit }) {
    const isActive = ref(false)
    const valUpdated = (val) => {
      emit('update:modelValue', val)
    }
    const modalValue = ref(props.modelValue)
    const initalAllOptions = props.options
    if (props.staticOption && props.staticOption.id) {
      initalAllOptions.results = initalAllOptions.results.filter((item) => {
        return (props.staticOption.id !== item.id)
      })
      initalAllOptions.results.unshift(props.staticOption)
    }
    const allOptions = ref(initalAllOptions)
    const isModalOpen = ref(false)
    const filteredOptions = ref(allOptions.value.results || [])
    const fetchLoading = ref(false)
    const filteredOptionsPagination = ref(null)
    const serachKeyword = ref(null)
    watch(
      () => props.modelValue,
      (newValue) => {
        modalValue.value = newValue
        if (props.emitObj) {
          let data = null
          if (filteredOptions.value && filteredOptions.value.length) {
            const index = filteredOptions.value.findIndex((item) => {
              return item.id === newValue
            })
            if (index > -1) {
              data = filteredOptions.value[index]
            }
          }
          emit('updateObj', data)
        }
      }
    )

    watch(
      () => props.options,
      (newValue) => {
        if (!newValue) return
        if (props.staticOption && props.staticOption.id) {
          const cleanedOptions = newValue.results.filter((item) => {
            return (props.staticOption.id !== item.id)
          })
          cleanedOptions.unshift(props.staticOption)
          allOptions.value.results = cleanedOptions
          filteredOptions.value = cleanedOptions
        } else {
          allOptions.value.results = newValue.results
          filteredOptions.value = newValue.results
        }
        Object.assign(allOptions.value.pagination, newValue.pagination)
      }
    )

    watch(
      () => props.staticOption,
      (newValue) => {
        if (newValue && newValue.id) {
          const cleanedOptions = allOptions.value.results.filter((item) => {
            return (newValue.id !== item.id)
          })
          cleanedOptions.unshift(newValue)
          allOptions.value.results = cleanedOptions
          filteredOptions.value = cleanedOptions
        }
      }
    )

    // watch(
    //   () => isActive.value, async (newValue) => {
    //     if (newValue && !fetchLoading.value && !initiallyLoaded.value) {
    //       await fetchOptions()
    //       initiallyLoaded.value = true
    //     }
    //   }
    // )

    const filterFn = (val, update) => {
      serachKeyword.value = val
      if (val === '') {
        update(() => {
          filteredOptions.value = allOptions.value.results
          filteredOptionsPagination.value = null
        })
        return
      }
      update(() => {
        const endpoint = props.endpoint + `?search=${val}`
        useApi(endpoint).then((data) => {
          filteredOptions.value = data.results
          filteredOptionsPagination.value = data.pagination
        }).catch((err) => {
          console.log(`Error While Fetching ${err}`)
        })
        // const needle = val.toLowerCase()
        // filteredOptions.value = allOptions.value.results.filter(
        //   (v) => v.name.toLowerCase().indexOf(needle) > -1
        // )
      })
    }

    const openModal = () => {
      // debugger
      isModalOpen.value = true
    }

    const handleModalSignal = (v) => {
      allOptions.value.results.push(v)
      isModalOpen.value = false
      emit('update:modelValue', v.id)
    }

    const closeModal = () => {
      isModalOpen.value = false
    }
    const fetchOptions = async () => {
      fetchLoading.value = true
      const queryObj = {}
      if (allOptions.value?.pagination?.page) queryObj.page = allOptions.value.pagination.page + 1
      if (props.fetchOnMount && modalValue.value) queryObj.id = modalValue.value
      const endpoint = withQuery(props.endpoint, queryObj)
      try {
        const data = await useApi(endpoint)
        if (data) {
          if (props.staticOption && props.staticOption.id) {
            const filteredOptions = data.results.filter((item) => {
              return (props.staticOption.id !== item.id)
            })
            allOptions.value.results.push(...filteredOptions)
          } else allOptions.value.results.push(...data.results)
          Object.assign(allOptions.value.pagination, data.pagination)
        }
        fetchLoading.value = false
      } catch (error) {
        console.log('Error While Fetching Options', error)
        fetchLoading.value = false
      }
      // .then((data) => {
      //   if (staticOptions && staticOptions.length) {
      //     allOptions.value.results.push(...props.staticOptions, ...data.results)
      //   } else allOptions.value.results.push(...data.results)
      //   Object.assign(allOptions.value.pagination, data.pagination)
      //   fetchLoading.value = false
      // }).catch((err) => {
      //   console.log('Error While Fetching Options', err)
      //   fetchLoading.value = false
      // })
    }

    // if (props.endpoint && !props.options?.results?.length > 0) {
    //   if (props.staticOptions && props.staticOptions.length) {
    //     fetchOptions(props.staticOptions)
    //   } else fetchOptions()
    // }

    const onScroll = (scrollData) => {
      if (filteredOptionsPagination.value) {
        if (scrollData.direction === 'increase' && scrollData.to > filteredOptions.value.length - 3 &&
          !(filteredOptionsPagination.value.page >= filteredOptionsPagination.value.pages) && !fetchLoading.value) {
          fetchLoading.value = true
          const endpoint = props.endpoint + `?search=${serachKeyword.value}&page=${filteredOptionsPagination.value.page + 1}`
          useApi(endpoint).then((data) => {
            filteredOptions.value.push(...data.results)
            filteredOptionsPagination.value = data.pagination
            fetchLoading.value = false
          }).catch((err) => {
            console.log(`Error While Fetching ${err}`)
            fetchLoading.value = false
          })
        }
      }
      else if (scrollData.direction === 'increase' && scrollData.to > allOptions.value.results.length - 3 &&
        allOptions.value.pagination.page !== allOptions.value.pagination.pages && !fetchLoading.value) {
        fetchOptions()
      }
    }
    if (props.fetchOnMount && props.endpoint) {
      if (modalValue.value) {
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
      onScroll,
      fetchLoading,
      isActive
    }
  },
}
</script>
