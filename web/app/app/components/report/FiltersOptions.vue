<script lang="ts">
import type { Ref } from 'vue'

export default defineNuxtComponent({
  props: {
    options: {
      type: Array<string>,
      default: () => {
        return {
          results: [],
          pagination: {},
        }
      },
    },
    modelValue: {
      type: Array,
      default: () => {
        return []
      },
    },
    label: {
      type: String,
      default: () => 'Statuses:',
    },
    endpoint: {
      type: String,
      required: true,
    },
    paginate: {
      type: Boolean,
      default: true,
    },
    fetchOnMount: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const avaliableOptions = ref(props.options?.results || [])
    const modalValueSelect = ref(null)
    const modalValue: Ref<Array<string>> = ref(props.modelValue)
    const removeOption = (id) => {
      if (typeof modalValue.value === 'string') {
        modalValue.value = []
      } else {
        const index: number = modalValue.value.findIndex(item => item === id)
        modalValue.value.splice(index, 1)
      }
    }
    watch(
      () => modalValue,
      (newValue) => {
        emit('update:modelValue', newValue)
      },
      { deep: true },
    )
    watch(
      () => modalValueSelect,
      (newValue) => {
        if (!newValue.value) return
        if (!modalValue.value.includes(newValue.value)) {
          if (typeof modalValue.value === 'string') modalValue.value = [`${modalValue.value}`]
          modalValue.value.push(newValue.value)
        }
      },
      { deep: true },
    )
    watch(
      () => props.modelValue,
      (newValue: Array<string>) => {
        if (typeof newValue === 'string') {
          modalValue.value = [`${newValue}`]
        } else {
          modalValue.value = newValue
        }
      },
      { deep: true },
    )
    const onNewSelect = (obj) => {
      if (!obj) return
      avaliableOptions.value.push(obj)
    }
    return {
      avaliableOptions,
      onNewSelect,
      modalValue,
      modalValueSelect,
      removeOption,
    }
  },
})
</script>

<template>
  <div class="q-pb-xl">
    <div v-if="modalValue && modalValue.length">
      <!-- <div class="text-grey-8 q-pb-md">{{ label }}</div> -->
      <div>
        <div v-if="typeof modalValue === 'string'" class="row q-gutter-sm q-pb-sm" style="max-height: 200px; overflow-x: auto; border-radius: 5px">
          <span class="q-px-sm" style="border-radius: 10px; padding: 2px 4px 0px 8px">
            {{ avaliableOptions[avaliableOptions.findIndex((item) => item.id == modalValue)]?.name }}
            <q-btn
              dense
              flat
              color="red"
              icon="cancel"
              @click.stop="() => removeOption(modalValue)"
            />
          </span>
        </div>
        <div v-else-if="modalValue.length > 0" class="row q-gutter-sm q-pb-sm" style="max-height: 200px; overflow-x: auto; border-radius: 5px">
          <span
            v-for="option in modalValue"
            :key="option"
            class="text-subtitl2 shadow-md rounded-md bg-blue-100"
            style="padding: 3px 4px 1px 8px"
          >
            {{ avaliableOptions[avaliableOptions.findIndex((item) => item.id == option)]?.name }}
            <q-btn
              dense
              flat
              class="q-pa-none q-ml-sm"
              color="red"
              icon="cancel"
              size="md"
              @click.stop="() => removeOption(option)"
            />
          </span>
        </div>
      </div>
    </div>
    <div>
      <n-auto-complete-v2
        v-if="paginate"
        v-model="modalValueSelect"
        :emit-obj="true"
        :endpoint="endpoint"
        :label="`${label}`"
        :options="options"
        @update-obj="onNewSelect"
      />
      <q-select
        v-else
        v-model="modalValueSelect"
        emit-value
        map-options
        option-label="name"
        option-value="id"
        :label="`${label}`"
        :options="options"
      />
    </div>
  </div>
</template>

<style>
.v-enter-active,
.v-leave-active {
  transition: opacity 0.1s linear;
  transition: width 0.1s linear;
  overflow: hidden;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
  width: 0;
}
</style>
