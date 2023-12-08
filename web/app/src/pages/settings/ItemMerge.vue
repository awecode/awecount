<template>
  <div>
    <q-card class="q-ma-md">
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Items Merge</span>
        </div>
      </q-card-section>
      <q-card-section class="q-pa-lg">
        <div class="flex justify-end">
          <q-btn color="blue" :loading="loading" @click="onSimilarFetch">Fetch Similar Groups</q-btn>
        </div>
        <div v-for="(modalValue, index) in modalValueArray" :key="index + Math.random()" class="mb-8">
          <h5 class="m-0">Group {{ index + 1 }}</h5>
          <ItemMergeGroup v-model="modalValueArray[index]" :itemOptions="itemOptions" @removeGroup="removeGroup(index)"
            :selectedItems="selectedItems">
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
const router = useRouter()
const modalValueArray = ref([{
  items: [null, null],
  config: {
    defaultItem: null
  }
}])
const loading = ref(false)
const $q = useQuasar()
const itemOptions = ref([])
useApi('v1/items/list/').then((data) => {
  itemOptions.value = data
})
const removeGroup = (index: number) => {
  modalValueArray.value.splice(index, 1)
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
  let filteredArray: Array<Record<string, Array<number> | Record<string, boolean>>> = []
  modalValueArray.value.forEach((group) => {
    const filterredItems = group.items.filter((item) => item !== null) as unknown as number[]
    const obj = { ...group }
    obj.items = filterredItems
    if (filterredItems.length > 1) {
      filteredArray.push(obj)
    }
  })
  if (filteredArray.length < 1) {
    $q.notify({
      color: 'red-6',
      message: 'Please Select at least two unique items in a Group.',
      icon: 'report_problem',
      position: 'top-right',
    })
    return
  }
  useApi('v1/items/merge/', {
    method: 'POST',
    body: filteredArray
  }).then((data) => {
    if (data.error) {
      if (data.error.items && data.error.items.length > 0) {
        modalValueArray.value = data.error.items
      }
      if (data.error.message) {
        $q.notify({
          color: 'warning',
          message: data.error.message,
          icon: 'report_problem',
          position: 'top-right',
        })
      }
    } else {
      $q.notify({
        color: 'green-6',
        message: 'Items Merged!',
        icon: 'check_circle',
        position: 'top-right',
      })
      router.push('/items/list/')
    }
  }).catch((error) => {
    $q.notify({
      color: 'red-6',
      message: error.status === 500 ? 'Some Went Wrong, Please contact us!' : '',
      icon: 'report_problem',
      position: 'top-right',
    })
  })
}
const selectedItems = computed(() => {
  const arrays: Array<Array<number | null>> = modalValueArray.value.map((value) => {
    return [...value.items]
  })
  const filteredArray = arrays.flat()
  return filteredArray.filter((id) => id !== null) as number[]
})
const onSimilarFetch = () => {
  loading.value = true
  useApi('v1/items/similar-items/').then((data) => {
    if (data.length < 1) {
      $q.notify({
        color: 'red-6',
        message: 'No matches Found!',
        icon: 'report_problem',
        position: 'top-right',
      })
      loading.value = false
      return
    }
    modalValueArray.value = data
    loading.value = false
  }).catch((error) => {
    $q.notify({
      color: 'red-6',
      message: error.status === 500 ? 'Some Went Wrong, Please contact us!' : '',
      icon: 'report_problem',
      position: 'top-right',
    })
    loading.value = false
  })
}
</script>
