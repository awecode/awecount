<script>
export default {
  setup() {
    const metaData = {
      title: 'Suppliers | Awecount',
    }
    useMeta(metaData)
    const route = useRoute()
    const endpoint = `/api/company/${route.params.company}/parties/suppliers/`
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
        field: 'dr',
        sortable: true,
      },
      {
        name: 'cr',
        label: 'Cr.',
        align: 'left',
        field: 'cr',
        sortable: true,
      },
      {
        name: 'balance',
        label: 'Balance',
        align: 'left',
        field: 'balance',
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
        color="green"
        :to="`/${$route.params.company}/party/create/`"
        label="New party"
        class="add-btn"
        icon-right="add"
      />
    </div>

    <q-table
      v-model:pagination="pagination"
      title="Accounts"
      :rows="rows"
      :columns="newColumn"
      :loading="loading"
      :filter="searchQuery"
      row-key="id"
      class="q-mt-md"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <q-input v-model="searchQuery" class="full-width search-input" dense debounce="500" placeholder="Search">
          <template #append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template #body-cell-email="props">
        <q-td :props="props">
          <a :href="'mailto:' + `${props.row.email}`" style="text-decoration: none" class="text-blue">{{ props.row.email
          }}</a>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('party.modify')"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-view-btn"
            style="font-size: 12px"
            label="edit"
            :to="`/${$route.params.company}/party/${props.row.id}/`"
          />
          <q-btn
            v-if="checkPermissions('party.view')"
            color="blue"
            class="q-py-none q-px-md font-size-sm l-edit-btn"
            style="font-size: 12px"
            label="Account"
            :to="`/${$route.params.company}/parties/account/${props.row.id}/`"
          />
        </q-td>
      </template>
      <template #body-cell-name="props">
        <q-td :props="props">
          <router-link
            v-if="checkPermissions('party.view')"
            :to="`/${$route.params.company}/parties/account/${props.row.id}/`"
            style="font-weight: 500; text-decoration: none"
            class="text-blue block"
          >
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
