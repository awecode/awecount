<template>
  <div>
    <div class="grid xl:grid-cols-6">
      <div class="flex flex-col gap-3 xl:col-span-4">
        <div v-for="(item, index) in modalValue.items" :key="index" class="flex">
          <div class="grow flex gap-2 items-center">
            <div class="grow-1">
              <n-auto-complete v-model="modalValue.items[index]" :options="itemOptions" label="Item"
                @update:model-value="(value) => onUpdate(value, selectedItems, index)"></n-auto-complete>
            </div>
            <q-btn color="red-5" outline icon="delete" :disable="modalValue.items.length < 2"
              @click="() => removeItem(index)"></q-btn>
          </div>
          <div class="w-36 flex items-center">
            <q-radio v-if="modalValue.items[index]" v-model="modalValue.config.defaultItem" :val="modalValue.items[index]"
              label="Default Item" />
          </div>
        </div>
      </div>
    </div>
    <div class="flex gap-4">
      <q-btn outline color="green" class="mt-8" @click="addItem">
        Add Items
      </q-btn>
      <q-btn outline color="red" class="mt-8" @click="emit('removeGroup')">
        Remove Group
      </q-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
const $q = useQuasar()
const props = defineProps({
  'modelValue': {
    type: [Object],
    default: () => {
      return [{
        items: [null, null],
        config: {
          defaultItem: null
        }
      }]
    },
  },
  'itemOptions': {
    type: [Array],
    default: () => [],
  },
  'selectedItems': {
    type: [Array],
    default: () => []
  }
})
const emit = defineEmits(['update:modelValue', 'removeGroup'])
const onUpdate = (value: number, selectedItems: Array<number>, index: number) => {
  if (selectedItems.includes(value)) {
    $q.notify({
      color: 'red-6',
      message: 'This Item has already been selected!',
      icon: 'report_problem',
      position: 'top-right',
    })
    nextTick(() => {
      modalValue.value.items[index] = null
    })
  }
}
const modalValue = ref(props.modelValue)
watch(modalValue, (newVal) => {
  emit('update:modelValue', newVal)
})
watch(props.modelValue, (newVal) => {
  modalValue.value = newVal
})
const removeItem = (index: number) => {
  if (modalValue.value.items.length < 2) return
  modalValue.value.items.splice(index, 1)
}
const addItem = () => {
  modalValue.value.items.push(null)
}
</script>
