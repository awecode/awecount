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
    <div v-if="checkPermissions('AccountOpeningBalanceCreate')" class="row">
      <q-btn color="green" :to="`/${$route.params.company}/items/opening/create/`" label="New Opening Balance" class="q-ml-auto add-btn" icon-right="add" />
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
      <template #top>
        <q-input v-model="searchQuery" dense debounce="500" placeholder="Search" class="full-width">
          <template #append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('AccountOpeningBalanceModify')"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm l-edit-btn"
            style="font-size: 12px"
            label="EDIT"
            :to="`/${$route.params.company}/items/opening/${props.row.id}/`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('ItemModify')"
            style="font-weight: 500; text-decoration: none"
            class="text-blue"
            :to="`/${$route.params.company}/items/${props.row.item_id}/`"
          >
            {{
              props.row.name
            }}
          </router-link>
          <span v-else>{{ props.row.name }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
