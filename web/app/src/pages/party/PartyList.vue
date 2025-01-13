<script>
const route = useRoute()
export default {
  setup() {
    const metaData = {
      title: 'Parties | Awecount',
    }
    useMeta(metaData)
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
        name: 'tax_registration_number',
        label: 'Pan No.',
        align: 'center',
        field: 'tax_registration_number',
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
      <q-btn v-if="checkPermissions('party.create')" color="green" :to="`/${$route.params.company}/party/create/`" label="New party" class="add-btn" icon-right="add" />
    </div>

    <q-table v-model:pagination="pagination" title="Accounts" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" row-key="id" class="q-mt-md" :rows-per-page-options="[20]" @request="onRequest">
      <template #top>
        <q-input v-model="searchQuery" dense debounce="500" placeholder="Search" class="full-width search-input">
          <template #append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('party.modify')" color="orange-6" class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn" style="font-size: 12px" label="edit" :to="`/${$route.params.company}/party/${props.row.id}/`" />
          <q-btn color="blue" class="q-py-none q-px-md font-size-sm l-view-btn" style="font-size: 12px" label="Account" :to="`/${$route.params.company}/parties/account/${props.row.id}/`" />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link v-if="checkPermissions('party.modify')" :to="`/${$route.params.company}/party/${props.row.id}/`" style="font-weight: 500; text-decoration: none" class="text-blue">
            {{ props.row.name }}
          </router-link>
          <span v-else>
            {{ props.row.name }}
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>
