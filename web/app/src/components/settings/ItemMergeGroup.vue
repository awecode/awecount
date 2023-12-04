<template>
  <div>
    <div class="grid lg:grid-cols-2">
      <div class="flex flex-col gap-3">
        <div v-for="(item, index) in modalValue.items" :key="index" class="flex gap-2 items-end">
          <q-select v-model="modalValue.items[index]" :options="itemOptions" option-value="id" option-label="name"
            map-options emit-value label="Item" class="grow-1" @update:model-value="(value) => onUpdate(value, selectedItems, index)"></q-select>
          <q-btn color="red-5" outline icon="delete" :disable="modalValue.items.length < 2"
            @click="() => removeItem(index)"></q-btn>
          <q-radio v-if="modalValue.items[index]" v-model="modalValue.defaultItem" :val="modalValue.items[index]" class="green" label="Default Item"/>
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
  'selectedItems' : {
    type: [Array],
    default: () => []
  }
})
const emit = defineEmits(['update:modelValue', 'removeGroup'])
const onUpdate = (value:number, selectedItems: Array<number>, index:number) => {
  if (selectedItems.includes(value)) {
    $q.notify({
      color: 'red-6',
      message: 'Please Select at least two unique items.',
      icon: 'report_problem',
      position: 'top-right',
    })
    modalValue.value.items[index] = null
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
