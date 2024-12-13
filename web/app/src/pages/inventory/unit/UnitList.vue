<template>
  <div class="q-pa-md">
    <div v-if="checkPermissions('UnitCreate')" class="row justify-between">
      <div></div>
      <q-btn color="green" to="/units/add/" label="New Unit" class="q-ml-lg add-btn" icon-right="add" />
    </div>

    <q-table :rows="rows" :columns="columns" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
      row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:body-cell-name="props">
        <q-td :props="props" style="padding: 0;">
          <router-link v-if="checkPermissions('UnitModify')" :to="`/units/${props.row.id}/`"
            style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px; text-decoration: none;"
            class="text-blue text-weight-medium">
            {{ props.row.name }}
          </router-link>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px;">
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
      title: 'Units | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/units/'
    return { ...useList(endpoint), checkPermissions }
  },
}
</script>
