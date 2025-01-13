<template>
  <q-card class="q-ma-md q-px-md">
    <q-card-section>
      <PlainNode v-for="data in treeData" :data="data" :key="data.id" :root="true"></PlainNode>
    </q-card-section>
  </q-card>
</template>

<script lang="ts">
import { Ref } from 'vue'
export default {
  setup() {
    const metaData = {
      title: 'Category Tree | Awecount',
    }
    useMeta(metaData)
    const treeData: Ref<Record<string, string | object> | null> = ref(null)
    useApi('v1/full-category-tree/')
      .then((data) => (treeData.value = data))
      .catch((err) => console.log(err))
    // TODO: add 404 error routing
    return { treeData }
  },
}
</script>
