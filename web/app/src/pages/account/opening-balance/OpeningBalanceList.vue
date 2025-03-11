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
      <q-btn
        v-if="checkPermissions('accountopeningbalance.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New Opening Balance"
        :to="`/${$route.params.company}/account/opening-balances/create`"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      title="Opening Balances"
      :columns="newColumn"
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
            v-if="checkPermissions('accountopeningbalance.update')"
            class="q-py-none q-px-md font-size-sm l-edit-btn"
            color="orange-6"
            label="Edit"
            style="font-size: 12px"
            :to="`/${$route.params.company}/account/opening-balances/${props.row.id}/edit`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('accountopeningbalance.update')"
            class="text-blue"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/account/opening-balances/${props.row.id}/edit`"
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
