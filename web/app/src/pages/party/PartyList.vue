<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn v-if="checkPermissions('PartyCreate')" color="green" to="/party/add/" label="New party" class="q-ml-lg"
        icon-right="add" />
    </div>

    <q-table title="Accounts" :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery"
      v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="full-width">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('PartyModify')" color="orange-6" class="q-py-none q-px-md font-size-sm q-mr-sm"
            style="font-size: 12px" label="edit" :to="`/party/${props.row.id}/`" />
          <q-btn color="blue" class="q-py-none q-px-md font-size-sm" style="font-size: 12px" label="Account"
            :to="`/parties/account/${props.row.id}/`" />
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
import checkPermissions from 'src/composables/checkPermissions'
export default {
  setup() {
    const metaData = {
      title: 'Parties | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/parties/'
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
        sortable: true
      },
      {
        name: 'address',
        label: 'Address',
        align: 'left',
        field: 'address',
        sortable: true
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
        sortable: true
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
