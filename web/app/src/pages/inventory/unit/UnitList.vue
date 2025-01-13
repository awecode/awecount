<script>
import checkPermissions from 'src/composables/checkPermissions'
import useList from '/src/composables/useList'

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

<template>
  <div class="q-pa-md">
    <div v-if="checkPermissions('UnitCreate')" class="row justify-between">
      <div></div>
      <q-btn
        class="q-ml-lg add-btn"
        color="green"
        icon-right="add"
        label="New Unit"
        to="/units/add/"
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
            v-if="checkPermissions('UnitModify')"
            class="text-blue text-weight-medium"
            style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px; text-decoration: none"
            :to="`/units/${props.row.id}/`"
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
