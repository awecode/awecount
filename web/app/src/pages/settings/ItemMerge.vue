<template>
  <div>
    <q-card class="q-ma-md">
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Items Merge</span>
        </div>
      </q-card-section>
      <q-card-section class="q-pa-lg">
        <div class="grid lg:grid-cols-2">
          <div class="flex flex-col gap-3">
            <div v-for="(modalValue, index) in modalValueArray" :key="index" class="flex gap-2 items-end">
              <q-select v-model="modalValueArray[index]" :options="itemOptions" option-value="id" option-label="name"
                map-options emit-value label="Item" class="grow-1"></q-select>
              <q-btn color="red-5" outline icon="delete" :disable="modalValueArray.length < 2"
                @click="removeItem(index)"></q-btn>
            </div>
          </div>
        </div>
        <div class="flex">
          <q-btn outline color="green" class="mt-8" @click="addItem">
            Add Items
          </q-btn>
        </div>
        <div class="flex justify-end">
          <q-btn color="green" class="mt-8" @click="onSubmit">
            Merge Items
          </q-btn>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
const modalValueArray = ref([null, null])
const $q = useQuasar()
const itemOptions = ref([])
useApi('v1/items/list/').then((data) => {
  itemOptions.value = data
})
const removeItem = (index: number) => {
  if (modalValueArray.value.length < 2) return
  modalValueArray.value.splice(index, 1)
}
const addItem = () => {
  modalValueArray.value.push(null)
}
const onSubmit = () => {
  let filteredArray = modalValueArray.value.filter((item) => item !== null)
  filteredArray = [...new Set(filteredArray)]
  if (filteredArray.length < 2) {
    $q.notify({
      color: 'red-6',
      message: 'Please Select at least two unique items.',
      icon: 'report_problem',
      position: 'top-right',
    })
    return
  }
  useApi('v1/items/merge/', {
    method: 'POST',
    body: filteredArray
  }).then(() => {
    $q.notify({
      color: 'green-6',
      message: 'Items Merged!',
      icon: 'check_circle',
      position: 'top-right',
    })
  }).catch((error) => {
    $q.notify({
      color: 'red-6',
      message: error,
      icon: 'report_problem',
      position: 'top-right',
    })
  })
}
</script>
