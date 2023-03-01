<template>
  <q-table
    :rows="props.fields?.rows"
    :columns="columns"
    :loading="loading"
    v-model:pagination="pagination"
    row-key="id"
    @request="onRequest"
    class="q-mt-md"
  >
    <template v-slot:body-cell-Tax="props">
      <q-td :props="props">
        {{ props.row.tax_scheme.rate }}% (<span class="text-uppercase">{{
          props.row.tax_scheme.friendly_name
        }}</span
        >)
      </q-td>
    </template>
    <template v-slot:body-cell-Amount="props">
      <q-td :props="props">
        {{ props.row.quantity * props.row.rate }}
      </q-td>
    </template>
    <template v-slot:row>
      <q-td> amonut </q-td>
    </template>
  </q-table>
</template>

<script>
export default {
  props: {
    fields: {
      type: Object,
      default: () => {
        return {}
      },
    },
  },
  setup(props, { emit }) {
    const columns = [
      {
        name: 'id',
        // label for header
        label: 'SN',

        // row Object property to determine value for this column
        field: '',
        // OR field: row => row.some.nested.prop,

        // (optional) if we use visible-columns, this col will always be visible
        required: true,

        // (optional) alignment
        align: 'left',

        // (optional) tell QTable you want this column sortable
        sortable: true,
        // (optional) compare function if you have
        // some custom data or want a specific way to compare two rows
        sort: (a, b, rowA, rowB) => parseInt(a, 10) - parseInt(b, 10),
        // function return value:
        //   * is less than 0 then sort a to an index lower than b, i.e. a comes first
        //   * is 0 then leave a and b unchanged with respect to each other, but sorted with respect to all different elements
        //   * is greater than 0 then sort b to an index lower than a, i.e. b comes first

        // (optional) override 'column-sort-order' prop;
        // sets column sort order: 'ad' (ascending-descending) or 'da' (descending-ascending)
        sortOrder: 'ad', // or 'da'

        // (optional) you can format the data with a function
        format: (val, row) => `${val}%`,
        // one more format example:
        // format: val => val
        //   ? /* Unicode checkmark checked */ "\u2611"
        //   : /* Unicode checkmark unchecked */ "\u2610",

        // body td:

        // or as Function --> classes: row => ... (return String)
      },
      {
        name: 'Particular',
        label: 'Particular',
        field: 'item_name',
        headerStyle: 'width: 400px; text-align: left',
        style: 'width: 400px; text-align: left',
      },
      {
        name: 'quantity',
        label: 'Qty',
        field: 'quantity',
        headerStyle: 'text-align: left',
        style: 'text-align: left',
      },
      {
        name: 'rate',
        label: 'Rate',
        field: 'rate',
        headerStyle: 'text-align: left',
        style: 'text-align: left',
      },
      {
        name: 'discount',
        label: 'Discount',
        field: 'discount',
        headerStyle: 'text-align: left',
        style: 'text-align: left',
      },
      {
        name: 'Tax',
        label: 'Tax',
        field: 'Tax',
        headerStyle: 'text-align: left',
        style: 'text-align: left',
      },
      {
        name: 'Amount',
        label: 'Amount',
        field: 'Amount',
        headerStyle: 'text-align: left',
        style: 'text-align: left',
      },
    ]
    return {
      props,
      columns,
    }
  },
}
</script>
