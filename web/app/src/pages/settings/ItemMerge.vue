<template>
  <div>
    <q-card class="q-ma-md">
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Items Merge</span>
        </div>
      </q-card-section>
      <q-card-section class="q-pa-lg">
        <div v-for="(modalValue, index) in modalValueArray" :key="index + Math.random()" class="mb-8">
          <h5 class="m-0">Group {{ index + 1 }}</h5>
          <ItemMergeGroup v-model="modalValueArray[index]" :itemOptions="itemOptions" @removeGroup="removeGroup(index)">
          </ItemMergeGroup>
        </div>
        <div class="flex justify-between">
          <q-btn color="green" class="mt-8" @click="addGroup">
            Add New Group
          </q-btn>
          <q-btn color="green" class="mt-8" @click="onSubmit">
            Merge Items
          </q-btn>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
const modalValueArray = ref([{
  items: [null, null],
  config: {
    defaultItem: null
  }
}])
const $q = useQuasar()
const itemOptions = ref([])
useApi('v1/items/list/').then((data) => {
  itemOptions.value = data
})
const removeGroup = (index: number) => {
  console.log('before', [...modalValueArray.value])
  modalValueArray.value.splice(index, 1)
  console.log('after', [...modalValueArray.value])
}
const addGroup = () => {
  modalValueArray.value.push({
    items: [null, null],
    config: {
      defaultItem: null
    }
  })
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
    body: modalValueArray.value
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
