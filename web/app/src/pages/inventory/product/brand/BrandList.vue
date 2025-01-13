<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn v-if="checkPermissions('BrandCreate')" color="green" to="/brand/add/" label="New brand" class="q-ml-lg add-btn" icon-right="add" />
    </div>
    <q-table :rows="rows" :columns="columns" :loading="loading" :filter="searchQuery" v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:body-cell-name="props">
        <q-td :props="props" style="padding: 0">
          <router-link v-if="checkPermissions('BrandModify')" :to="`/brand/${props.row.id}/`" style="text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px" class="text-blue">
            {{ props.row.name }}
          </router-link>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px">
            {{ props.row.name }}
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  setup() {
    const metaData = {
      title: 'Brands | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/brands/'
    return { ...useList(endpoint), checkPermissions }
  },
}
</script>
