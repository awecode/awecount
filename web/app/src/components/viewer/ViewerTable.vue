<template>
  <!-- <template v-slot:body-cell-Tax="props">
      <q-td :props="props">
        {{ props.row.tax_scheme.rate }}% (<span class="text-uppercase">{{
          props.row.tax_scheme.friendly_name
        }}</span>)
      </q-td>
    </template>
    <template v-slot:body-cell-Amount="props">
      <q-td :props="props">
        {{ props.row.quantity * props.row.rate }}
      </q-td>
    </template> -->
  <q-markup-table flat bordered>
    <thead>
      <q-tr class="text-left">
        <q-th> SN </q-th>
        <q-th> Particular </q-th>
        <q-th> Qty </q-th>
        <q-th> Rate </q-th>
        <q-th> Discount </q-th>
        <q-th class="text-right"> Tax </q-th>
        <q-th class="text-right"> Amount </q-th>
      </q-tr>
    </thead>
    <tbody class="text-left">
      <q-tr v-for="(row, index) in fields?.rows" :key="index">
        <q-td>
          {{ index + 1 }}
        </q-td>
        <q-td>
          {{ row.item_name }}
        </q-td>
        <q-td>
          {{ row.quantity }}
        </q-td>
        <q-td> {{ row.rate }} </q-td><q-td> {{ row.discount }} </q-td
        ><q-td class="text-right">
          {{ row.tax_scheme.rate }}% (<span class="text-uppercase">{{
            row.tax_scheme.friendly_name
          }}</span
          >) </q-td
        ><q-td class="text-right">
          {{ row.rate * row.quantity }}
        </q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td><q-td> </q-td><q-td class="text-right"> Sub Total </q-td
        ><q-td class="text-right">{{ fields?.meta_sub_total }}</q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td><q-td> </q-td><q-td class="text-right"> Discount </q-td
        ><q-td class="text-right">{{ fields?.meta_discount }}</q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td><q-td> </q-td><q-td class="text-right"> Tax </q-td
        ><q-td class="text-right">{{ fields?.meta_sub_total }}</q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td><q-td> </q-td><q-td class="text-right"> Total </q-td
        ><q-td class="text-right">{{ fields?.total_amount }}</q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <td></td>
        <td>
          <span> {{ numberToText(fields?.total_amount) }} </span>
        </td>
      </q-tr>
    </tbody>
  </q-markup-table>
</template>

<script>
import numberToText from 'src/composables/numToText'
export default {
  props: {
    fields: {
      type: Object,
      default: () => {
        return {}
      },
    },
  },
  setup(props) {
    // const columns = [
    //   {
    //     name: 'index',
    //     // label for header
    //     label: 'SN',

    //     // row Object property to determine value for this column
    //     field: 'index',
    //     // OR field: row => row.some.nested.prop,

    //     // (optional) if we use visible-columns, this col will always be visible
    //     required: true,

    //     // (optional) alignment
    //     align: 'left',
    //   },
    //   {
    //     name: 'Particular',
    //     label: 'Particular',
    //     field: 'item_name',
    //     headerStyle: 'width: 400px; text-align: left',
    //     style: 'width: 400px; text-align: left',
    //   },
    //   {
    //     name: 'quantity',
    //     label: 'Qty',
    //     field: 'quantity',
    //     headerStyle: 'text-align: left',
    //     style: 'text-align: left',
    //   },
    //   {
    //     name: 'rate',
    //     label: 'Rate',
    //     field: 'rate',
    //     headerStyle: 'text-align: left',
    //     style: 'text-align: left',
    //   },
    //   {
    //     name: 'discount',
    //     label: 'Discount',
    //     field: 'discount',
    //     headerStyle: 'text-align: left',
    //     style: 'text-align: left',
    //   },
    //   {
    //     name: 'Tax',
    //     label: 'Tax',
    //     field: 'Tax',
    //     headerStyle: 'text-align: left',
    //     style: 'text-align: left',
    //   },
    //   {
    //     name: 'Amount',
    //     label: 'Amount',
    //     field: 'Amount',
    //     headerStyle: 'text-align: left',
    //     style: 'text-align: left',
    //   },
    // ]
    return {
      props,
      // columns,
      numberToText,
    }
  },
}
</script>
