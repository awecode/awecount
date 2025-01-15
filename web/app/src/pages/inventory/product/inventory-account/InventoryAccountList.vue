<script>
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/inventory-account/`
    const columnList = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
      },
      {
        name: 'opening_balance',
        label: 'Opening Balance',
        align: 'left',
        field: 'opening_balance',
      },
      {
        name: 'current_balance',
        label: 'Current Balance',
        align: 'left',
        field: 'current_balance',
      },
      {
        name: 'code',
        label: 'Code.',
        align: 'left',
        field: 'code',
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'left',
      },
    ]
    const metaData = {
      title: 'Inventory Accounts | Awecount',
    }
    useMeta(metaData)
    return { ...useList(endpoint), columnList, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      :columns="columnList"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <q-input
          v-model="searchQuery"
          dense
          class="full-width search-input"
          debounce="500"
          placeholder="Search"
        >
          <template #append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('inventoryaccount.view')"
            class="q-py-none q-px-md font-size-sm l-view-btn"
            color="blue"
            label="view"
            style="font-size: 12px"
            :to="`/${$route.params.company}/inventory-account/detail/${props.row.id}`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('inventoryaccount.view')"
            class="text-blue font-medium"
            style="text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/inventory-account/detail/${props.row.id}`"
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
