<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn
        color="green"
        to="/party/add/"
        label="New party"
        class="q-ml-lg"
        icon-right="add"
      />
    </div>

    <q-table
      title="Accounts"
      :rows="rows"
      :columns="newColumn"
      :loading="loading"
      :filter="searchQuery"
      v-model:pagination="pagination"
      row-key="id"
      @request="onRequest"
      class="q-mt-md"
      :rows-per-page-options="[20]"
    >
      <template v-slot:top-right>
        <q-input
          borderless
          dense
          debounce="500"
          v-model="searchQuery"
          placeholder="Search"
        >
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center">
            <div
              class="text-white text-subtitle2 row items-center justify-center"
              :class="
                props.row.status == 'Issued'
                  ? 'bg-blue'
                  : props.row.status == 'Paid'
                  ? 'bg-green'
                  : props.row.status == 'Draft'
                  ? 'bg-orange'
                  : 'bg-red'
              "
              style="border-radius: 30px; padding: 5px 15px"
            >
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            color="orange-6"
            class="q-py-none q-px-md font-size-sm q-mr-sm"
            style="font-size: 12px"
            label="edit"
            :to="`/party/${props.row.id}/`"
          />
          <q-btn
            :disable="props.row.status !== 'Cancelled'"
            color="blue"
            class="q-py-none q-px-md font-size-sm"
            style="font-size: 12px"
            label="Journal entries"
            :to="`/journal-entries/tax-payments/${props.row.id}/`"
          />
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
export default {
  setup() {
    const endpoint = '/v1/parties/'
    const listData = useList(endpoint)
    const newColumn = [
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
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
        align: 'center',
        field: 'tax_registration_number',
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    return { ...listData, newColumn }
  },
}
</script>
