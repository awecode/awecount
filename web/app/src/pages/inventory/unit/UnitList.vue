<script>
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

export default {
  setup() {
    const route = useRoute()
    const metaData = {
      title: 'Units | Awecount',
    }
    useMeta(metaData)
    const endpoint = `/api/company/${route.params.company}/units/`
    return { ...useList(endpoint), checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div v-if="checkPermissions('unit.create')" class="row justify-between">
      <div></div>
      <q-btn
        class="q-ml-lg add-btn"
        color="green"
        icon-right="add"
        label="New Unit"
        :to="`/${$route.params.company}/inventory/units/create`"
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
            v-if="checkPermissions('unit.update')"
            class="text-blue text-weight-medium"
            style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px; text-decoration: none"
            :to="`/${$route.params.company}/inventory/units/${props.row.id}/edit`"
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
