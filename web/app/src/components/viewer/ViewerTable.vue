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
        <q-th data-testid="SN" > SN </q-th>
        <q-th data-testid="Particular" > Particular </q-th>
        <q-th data-testid="Qty" > Qty </q-th>
        <q-th data-testid="Rate" > Rate </q-th>
        <q-th data-testid="Discount" > Discount </q-th>
        <q-th data-testid="Tax"  class="text-right"> Tax </q-th>
        <q-th data-testid="Amount"  class="text-right"> Amount </q-th>
      </q-tr>
    </thead>
    <tbody class="text-left">
      <q-tr v-for="(row, index) in fields?.rows" :key="index">
        <q-td>
          {{ index + 1 }}
        </q-td>
        <q-td>
          {{ row.item_name }} <br>
          <span v-if="row.description" style="font-size: 11px;" class="text-grey-8">
            <div v-for="(des, index) in row.description.split('\n')" :key="index" class="whitespace-normal">
              {{ des }}
            </div>
          </span>
        </q-td>
        <q-td>
          <span v-if="props.showRateQuantity">{{ row.quantity }} <span class="text-grey-9">
              ({{ row.unit_name }})</span></span>
        </q-td>
        <q-td> <span v-if="props.showRateQuantity">{{ $nf(row.rate) }}</span> </q-td>
        <q-td>
          <span v-if="row.discount_obj"> {{ $nf(row.discount_obj.value) }} {{ row.discount_obj.type === 'Percent' ? '%' : '-/'}} </span>
          <span v-else-if="row.discount_type">{{ $nf(row.discount) }} {{ row.discount_type === 'Percent' ? '%' : '-/'}}</span>
        </q-td>
        <!-- <q-td> {{ row.discount }} </q-td> -->
        <q-td class="text-right">
          {{ row.tax_scheme.rate }}% (<span class="text-uppercase">{{
            row.tax_scheme.friendly_name
          }}</span>) </q-td><q-td class="text-right">
          {{ $nf(row.rate * row.quantity) }}
        </q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td><q-td> </q-td><q-td class="text-right"> Sub Total </q-td><q-td class="text-right">{{
          formatNumberWithComma(fields?.voucher_meta.sub_total) }}</q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td><q-td> </q-td><q-td class="text-right"> Discount </q-td><q-td class="text-right">{{
          formatNumberWithComma(fields?.voucher_meta.discount) }}</q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td><q-td> </q-td><q-td class="text-right"> {{ getTaxname }} </q-td><q-td class="text-right" data-testid="tax">{{
          formatNumberWithComma(fields?.voucher_meta.tax)
        }}</q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td>
        <q-td> </q-td><q-td> </q-td><q-td class="text-right"> Total </q-td><q-td class="text-right">{{
          formatNumberWithComma(fields?.voucher_meta.grand_total) }}</q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <td></td>
        <td colspan="6">
          <span style="white-space: wrap;">In Words: {{ numberToText(fields?.voucher_meta.grand_total) }} </span>
        </td>
      </q-tr>
    </tbody>
  </q-markup-table>
</template>

<script>
import numberToText from 'src/composables/numToText'
import formatNumberWithComma from 'src/composables/formatNumberWithComma'
export default {
  props: {
    fields: {
      type: Object,
      default: () => {
        return {}
      },
    },
    showRateQuantity: {
      type: Boolean,
      default: () => true,
    },
  },
  setup(props) {
    const getTaxname = computed(() => {
      let sameScheme = null
      let tax_scheme = null
      if (props.fields.rows && props.fields.rows.length) {
        props.fields.rows.forEach(item => {
          if (sameScheme !== false && item.tax_scheme) {
            if (sameScheme === null && item.tax_scheme && item.tax_scheme.rate != 0) {
              sameScheme = item.tax_scheme.id
              tax_scheme = item.tax_scheme
            } else if (sameScheme === item.tax_scheme?.id || item.tax_scheme.rate === 0) {
            } else sameScheme = false
          }
        });
        if (typeof sameScheme === 'number' && tax_scheme) {
          return (`${tax_scheme.friendly_name || ''}` +
            ' @ ' +
            `${tax_scheme.rate || ''}` +
            '%')
        } else {
          return 'Tax'
        }
      } else return ''
    })
    return {
      props,
      // columns,
      numberToText,
      formatNumberWithComma,
      getTaxname
    }
  },
}
</script>
