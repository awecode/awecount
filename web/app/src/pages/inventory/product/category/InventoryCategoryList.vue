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
    <div v-if="checkPermissions('CategoryCreate')" class="row justify-end">
      <q-btn color="green" :to="`/${$route.params.company}/inventory-category/add/" label="New Category" class="q-ml-lg add-btn" icon-right="add`" />
    </div>
    <q-table
      v-model:pagination="pagination"
      :rows="rows"
      :columns="newColumns"
      :loading="loading"
      :filter="searchQuery"
      row-key="id"
      class="q-mt-md"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            color="blue"
            class="q-py-none q-px-md font-size-sm"
            style="font-size: 12px"
            label="view"
            :to="`/${$route.params.company}/account/${props.row.id}/view/`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('CategoryModify')"
            class="text-blue"
            style="text-decoration: none"
            :to="`/${$route.params.company}/inventory-category/${props.row.id}/`"
          >
            {{
              props.row.name }}
          </router-link>
          <span v-else>{{ props.row.name }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
