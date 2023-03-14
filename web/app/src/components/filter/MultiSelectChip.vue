<template>
  <div class="row q-gutter-sm q-pt-md">
    <q-btn
      @click="() => onStatusClick(statuses)"
      style="border-radius: 1rem"
      class="q-py-sm q-px-md"
      v-for="(statuses, index) in options"
      :key="index"
      :class="
        modalValue.includes(statuses)
          ? 'bg-blue-1 text-blue-9'
          : 'bg-grey-4 text-grey-9'
      "
    >
      <!-- TODO: add animation -->
      <q-icon
        v-if="modalValue.includes(statuses)"
        name="check"
        size="sm"
        color="blue"
        class="q-mr-xs"
      ></q-icon>
      <span>
        {{ statuses }}
      </span>
    </q-btn>
  </div>
</template>

<script lang="ts">
import { Ref } from 'vue'

export default {
  props: {
    options: {
      type: Array<string>,
      default: () => [],
    },
    modelValue: {
      type: Array,
      default: () => {
        return []
      },
    },
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const modalValue: Ref<Array<string>> = ref(props.modelValue)
    const onStatusClick = (status: string) => {
      const index: number = modalValue.value.findIndex(
        (item) => item === status
      )
      if (index >= 0) {
        modalValue.value.splice(index, 1)
      } else {
        modalValue.value.push(status)
      }
      console.log(modalValue.value)
    }
    watch(
      () => modalValue,
      (newValue) => {
        emit('update:modelValue', newValue)
      },
      { deep: true }
    )
    watch(
      () => props.modelValue,
      (newValue: Array<string>) => {
        // if (typeof newValue === 'string') {
        //   console.log('string', newValue)
        // }
        modalValue.value = newValue
      },
      { deep: true }
    )
    return {
      modalValue,
      onStatusClick,
    }
  },
}
</script>
