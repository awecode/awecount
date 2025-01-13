<script>
import checkPermissions from 'src/composables/checkPermissions'
import useList from '/src/composables/useList'

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

<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn
        v-if="checkPermissions('BrandCreate')"
        class="q-ml-lg add-btn"
        color="green"
        icon-right="add"
        label="New brand"
        to="/brand/add/"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      :columns="columns"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('BrandModify')"
            class="text-blue"
            style="text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/brand/${props.row.id}/`"
          >
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
