<script>
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/inventory-categories/`
    const metaData = {
      title: 'Inventory Category | Awecount',
    }
    useMeta(metaData)
    const newColumns = [
      {
        name: 'code',
        label: 'Code.',
        align: 'left',
        field: 'code',
      },
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
      },
    ]
    return { ...useList(endpoint), newColumns, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div v-if="checkPermissions('category.create')" class="row justify-end">
      <q-btn
        class="q-ml-lg add-btn"
        color="green"
        icon-right="add"
        label="New Category"
        :to="`/${$route.params.company}/inventory-category/create/`"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      :columns="newColumns"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            class="q-py-none q-px-md font-size-sm"
            color="blue"
            label="view"
            style="font-size: 12px"
            :to="`/${$route.params.company}/account/${props.row.id}/view/`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('category.modify')"
            class="text-blue"
            style="text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/inventory-category/${props.row.id}/`"
          >
            {{ props.row.name }}
          </router-link>
          <span
            v-else
            style="display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
          >
            {{ props.row.name }}
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
