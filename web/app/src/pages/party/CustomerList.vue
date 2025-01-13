<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn v-if="checkPermissions('PartyCreate')" color="green" to="/party/add/" label="New party" class="add-btn" icon-right="add" />
    </div>

    <q-table title="Accounts" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <q-input class="full-width search-input" dense debounce="500" v-model="searchQuery" placeholder="Search">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body-cell-email="props">
        <q-td :props="props">
          <a :href="'mailto:' + `${props.row.email}`" style="text-decoration: none" class="text-blue">{{ props.row.email }}</a>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('PartyModify')" color="orange-6" class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn" style="font-size: 12px" label="edit" :to="`/party/${props.row.id}/`" />
          <q-btn color="blue" class="q-py-none q-px-md font-size-sm l-view-btn" v-if="checkPermissions('PartyView')" style="font-size: 12px" label="Account" :to="`/parties/account/${props.row.id}/`" />
        </q-td>
      </template>
      <template v-slot:body-cell-name="props">
        <q-td :props="props" style="padding: 0">
          <router-link v-if="checkPermissions('PartyView')" :to="`/parties/account/${props.row.id}/`" style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 16px 8px 8px 16px" class="text-blue block">
            {{ props.row.name }}
          </router-link>
          <span v-else style="display: flex; align-items: center; height: 100%; padding: 16px 8px 8px 16px">
            {{ props.row.name }}
          </span>
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
export default {
  setup() {
    const metaData = {
      title: 'Customers | Awecount',
    }
    useMeta(metaData)
    const endpoint = 'v1/parties/customers/'
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
        align: 'left',
        field: 'tax_registration_number',
        sortable: true,
      },
      {
        name: 'dr',
        label: 'Dr.',
        align: 'left',
        field: (row) => Math.round(row.dr * 100) / 100,
        sortable: true,
      },
      {
        name: 'cr',
        label: 'Cr.',
        align: 'left',
        field: (row) => Math.round(row.cr * 100) / 100,
        sortable: true,
      },
      {
        name: 'balance',
        label: 'Balance',
        align: 'left',
        field: (row) => Math.round(row.balance * 100) / 100,
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
