<script>
export default {
  setup() {
    const metaData = {
      title: 'Account Opening Balances | Awecount',
    }
    useMeta(metaData)

    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/account-opening-balance/`

    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
      },
      {
        name: 'opening_dr',
        label: 'Opening Dr',
        align: 'left',
        field: 'opening_dr',
        sortable: true,
      },
      {
        name: 'opening_cr',
        label: 'Opening Cr',
        align: 'left',
        field: 'opening_cr',
        sortable: true,
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    return { ...useList(endpoint), newColumn, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn v-if="checkPermissions('accountopeningbalance.create')" color="green" :to="`/${$route.params.company}/account-opening-balance/create/`" label="New Opening Balance" class="add-btn" icon-right="add" />
    </div>
    <q-table v-model:pagination="pagination" title="Opening Balances" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" row-key="id" class="q-mt-md" :rows-per-page-options="[20]" @request="onRequest">
      <template #top>
        <q-input v-model="searchQuery" dense debounce="500" placeholder="Search" class="full-width search-input">
          <template #append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('accountopeningbalance.modify')" label="Edit" color="orange-6" class="q-py-none q-px-md font-size-sm l-edit-btn" style="font-size: 12px" :to="`/${$route.params.company}/account-opening-balance/${props.row.id}/`" />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link v-if="checkPermissions('accountopeningbalance.modify')" style="font-weight: 500; text-decoration: none" class="text-blue" :to="`/${$route.params.company}/account-opening-balance/${props.row.id}/`">
            {{ props.row.name }}
          </router-link>
          <span v-else>{{ props.row.name }}</span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
