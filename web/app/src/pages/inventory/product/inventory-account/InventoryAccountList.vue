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
      :rows="rows"
      :columns="columnList"
      :loading="loading"
      :filter="searchQuery"
      row-key="id"
      class="q-mt-md"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <q-input v-model="searchQuery" dense debounce="500" placeholder="Search" class="full-width search-input">
          <template #append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('inventoryaccount.view')"
            color="blue"
            class="q-py-none q-px-md font-size-sm l-view-btn"
            style="font-size: 12px"
            label="view"
            :to="`/${$route.params.company}/inventory-account/detail/${props.row.id}`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('inventoryaccount.view')"
            :to="`/${$route.params.company}/inventory-account/detail/${props.row.id}`"
            class="no-underline font-medium text-blue"
          >
            {{ props.row.name }}
          </router-link>
          <span v-else>{{ props.row.name }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
