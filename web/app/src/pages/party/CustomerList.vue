<script>
export default {
  setup() {
    const metaData = {
      title: 'Customers | Awecount',
    }
    const route = useRoute()
    useMeta(metaData)
    const endpoint = `/api/company/${route.params.company}/parties/customers/`
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
        field: row => Math.round(row.dr * 100) / 100,
        sortable: true,
      },
      {
        name: 'cr',
        label: 'Cr.',
        align: 'left',
        field: row => Math.round(row.cr * 100) / 100,
        sortable: true,
      },
      {
        name: 'balance',
        label: 'Balance',
        align: 'left',
        field: row => Math.round(row.balance * 100) / 100,
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
        :to="`/${$route.params.company}/party/create/`"
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
      <template #body-cell-email="props">
        <q-td :props="props">
          <a class="text-blue" style="text-decoration: none" :href="'mailto:' + `${props.row.email}`">{{ props.row.email }}</a>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('party.modify')"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn"
            color="orange-6"
            label="edit"
            style="font-size: 12px"
            :to="`/${$route.params.company}/party/${props.row.id}/`"
          />
          <q-btn
            v-if="checkPermissions('party.view')"
            class="q-py-none q-px-md font-size-sm l-view-btn"
            color="blue"
            label="Account"
            style="font-size: 12px"
            :to="`/${$route.params.company}/parties/account/${props.row.id}/`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td style="padding: 0" :props="props">
          <router-link
            v-if="checkPermissions('party.view')"
            class="text-blue block"
            style="font-weight: 500; text-decoration: none; display: flex; align-items: center; height: 100%; padding: 8px 8px 8px 16px"
            :to="`/${$route.params.company}/parties/account/${props.row.id}/`"
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
