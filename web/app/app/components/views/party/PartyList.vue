<script>
export default {
  setup() {
    const route = useRoute()
    const metaData = {
      title: 'Parties | Awecount',
    }
    useHead(metaData)
    const endpoint = `/api/company/${route.params.company}/parties/`
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
        sortable: true,
      },
      {
        name: 'address',
        label: 'Address',
        align: 'left',
        field: 'address',
        sortable: true,
      },
      {
        name: 'contact_no',
        label: 'Contact No',
        align: 'left',
        field: 'contact_no',
      },
      {
        name: 'email',
        label: 'Email',
        align: 'left',
        field: 'email',
      },
      {
        name: 'tax_identification_number',
        label: 'Pan No.',
        align: 'center',
        field: 'tax_identification_number',
        sortable: true,
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    return { ...listData, newColumn, checkPermissions }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn
        v-if="checkPermissions('party.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        label="New party"
        :to="`/${$route.params.company}/crm/parties/create`"
      />
    </div>

    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      title="Accounts"
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
            v-if="checkPermissions('party.update')"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn"
            color="orange-6"
            label="edit"
            style="font-size: 12px"
            :to="`/${$route.params.company}/crm/parties/${props.row.id}/edit`"
          />
          <q-btn
            class="q-py-none q-px-md font-size-sm l-view-btn"
            color="blue"
            label="Account"
            style="font-size: 12px"
            :to="`/${$route.params.company}/crm/parties/${props.row.id}/account`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('party.update')"
            class="text-blue"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/crm/parties/${props.row.id}/edit`"
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
