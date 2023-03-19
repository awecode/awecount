<template>
  <div class="q-pa-md">
    <div class="row justify-between">
      <div></div>
      <q-btn
        color="green"
        to="/account/add/"
        label="New Account"
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
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <!-- <q-btn icon="visibility" color="blue" dense flat to="" /> -->
          <q-btn
            color="blue"
            class="q-py-none q-px-md font-size-sm q-mr-md"
            style="font-size: 12px"
            label="View"
            :to="`/account/${props.row.id}/view/`"
          />
          <q-btn
            label="Edit"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm"
            style="font-size: 12px"
            :to="`/account/${props.row.id}/edit/`"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-category="props">
        <q-td :props="props">
          <router-link
            style="font-weight: 500; text-decoration: none"
            class="text-blue"
            :to="`/account/category/${props.row.category.id}/edit/`"
            >{{ props.row.category.name }}</router-link
          >
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script>
import useList from '/src/composables/useList'
export default {
  setup() {
    const endpoint = '/v1/accounts/'
    const newColumn = [
      {
        name: 'code',
        label: 'Code',
        align: 'left',
        field: 'code',
      },
      {
        name: 'name',
        label: 'Name',
        align: 'left',
        field: 'name',
      },
      {
        name: 'category',
        label: 'Category',
        align: 'left',
        field: 'category',
      },
      {
        name: 'dr',
        label: 'Dr',
        align: 'left',
        field: 'dr',
      },
      {
        name: 'cr',
        label: 'Cr',
        align: 'left',
        field: 'cr',
      },
      {
        name: 'balance',
        label: 'Balance',
        align: 'left',
        field: 'computed_balance',
      },
      {
        name: 'actions',
        label: 'Actions',
        align: 'center',
      },
    ]
    return { ...useList(endpoint), newColumn }
  },
}
</script>
