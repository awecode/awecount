<script>
import checkPermissions from 'src/composables/checkPermissions'
import useList from 'src/composables/useList'

export default {
  setup() {
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/item-opening-balance/`
    const metaData = {
      title: 'Stock Opening | Awecount',
    }
    const newColumns = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
      },
      {
        name: 'balance',
        label: 'Opening Balance',
        align: 'left',
        field: 'opening_balance',
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'left',
      },
    ]
    useMeta(metaData)
    return { ...useList(endpoint), checkPermissions, newColumns }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div v-if="checkPermissions('accountopeningbalance.create')" class="row">
      <q-btn
        class="q-ml-auto add-btn"
        color="green"
        icon-right="add"
        label="New Opening Balance"
        :to="`/${$route.params.company}/items/opening/create/`"
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
      <template #top>
        <q-input
          v-model="searchQuery"
          dense
          class="full-width"
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
            v-if="checkPermissions('accountopeningbalance.modify')"
            class="q-py-none q-px-md font-size-sm l-edit-btn"
            color="orange-6"
            label="EDIT"
            style="font-size: 12px"
            :to="`/${$route.params.company}/items/opening/${props.row.id}/`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('item.modify')"
            class="text-blue"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/items/${props.row.item_id}/`"
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
