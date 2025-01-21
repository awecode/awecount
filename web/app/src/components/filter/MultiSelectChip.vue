<script lang="ts">
import type { Ref } from 'vue'

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
    label: {
      type: String,
      default: () => 'Statuses:',
    },
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const modalValue: Ref<Array<string>> = ref(props.modelValue)
    const onStatusClick = (status: string) => {
      if (typeof modalValue.value === 'string') {
        if (modalValue.value === status) {
          modalValue.value = []
        } else {
          modalValue.value = [status, modalValue.value]
        }
      } else {
        const index: number = modalValue.value.findIndex(item => item === status)
        if (index >= 0) {
          modalValue.value.splice(index, 1)
        } else {
          modalValue.value.push(status)
        }
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
      () => props.modelValue,
      (newValue: Array<string>) => {
        // if (typeof newValue === 'string') {
        //   console.log('string', newValue)
        // }
        modalValue.value = newValue
      },
      { deep: true },
    )
    return {
      modalValue,
      onStatusClick,
    }
  },
}
</script>

<template>
  <div class="q-pt-md">
    <div class="text-grey-8 q-pb-xs">
      {{ label }}
    </div>
    <div class="row q-gutter-sm">
      <!-- style="border-radius: 1rem; padding: 4px 12px" -->
      <q-btn
        v-for="(statuses, index) in options"
        :key="index"
        class="text-subtitle2"
        size="sm"
        style="border-radius: 1rem; padding: 4px 12px"
        :class="modalValue.includes(statuses) ? 'bg-blue-1 text-blue-9' : 'bg-grey-4 text-grey-9'"
        @click="() => onStatusClick(statuses)"
      >
        <!-- TODO: add animation -->
        <div class="row items-center">
          <Transition>
            <q-icon
              v-if="modalValue.includes(statuses)"
              class="q-mr-xs"
              color="blue"
              name="check"
              size="sm"
              style="height: 22px"
            />
          </Transition>
          <span style="font-size: 0.85rem; text-transform: capitalize">
            {{ statuses }}
          </span>
        </div>
      </q-btn>
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
