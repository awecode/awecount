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
      :columns="columns"
      :loading="loading"
      :filter="searchQuery"
      v-model:pagination="pagination"
      row-key="id"
      @request="onRequest"
      class="q-mt-md"
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
            class="q-mr-md"
            label="View"
            :to="`/account/${props.row.id}/view/`"
          />
          <q-btn
            icon="edit"
            color="amber"
            dense
            flat
            :to="`/account/${props.row.id}/edit/`"
          />
          <!-- <q-btn
            icon="delete"
            color="red"
            dense
            flat
            @click="confirmDeletion(props.row.id)"
          /> -->
          <!-- {{ props }} -->
        </q-td>
      </template>
      <template v-slot:body-cell-category="props">
        <q-td :props="props">
          <router-link
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
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
      },
      {
        name: 'voucher_no',
        label: 'Bill No',
        align: 'left',
        field: 'voucher_no',
      },
      {
        name: 'sellers_name',
        label: "Seller's Name",
        align: 'left',
        field: 'sellers_name',
      },
      {
        name: 'sellers_pan',
        label: 'Tax No.',
        align: 'left',
        field: 'sellers_pan',
      },
      {
        name: 'total_sales',
        remove: true,
        label: 'Total Purchases',
        align: 'left',
        field: (row) => row.voucher_meta.grand_total,
      },
      {
        name: 'non_taxable_sales',
        remove: true,
        label: 'Non Taxable Sales',
        align: 'left',
        field: (row) => row.voucher_meta.non_taxable,
      },
      {
        name: 'import_purchases',
        remove: true,
        label: 'Import Purchases',
        align: 'left',
        field: '',
      },
      // TODO: add export sales
      {
        name: 'discount',
        label: 'Discount',
        align: 'left',
        field: (row) => row.voucher_meta.discount,
        remove: true,
      },
      {
        name: 'amount',
        label: 'Amount',
        align: 'left',
        field: (row) => row.voucher_meta.taxable,
      },
      {
        name: 'tax',
        label: 'Tax',
        align: 'left',
        field: (row) => row.voucher_meta.tax,
      },
    ]
    return { ...useList(endpoint) }
  },
}
</script>
