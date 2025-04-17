<script>
import Decimal from 'decimal.js'
import formatNumberWithComma from 'src/composables/formatNumberWithComma'
import numberToText from 'src/composables/numToText'

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
    const tax = computed(() => {
      let sameScheme = null
      let tax_scheme = null
      if (props.fields.rows && props.fields.rows.length) {
        props.fields.rows.forEach((item) => {
          if (sameScheme !== false && item.tax_scheme) {
            if (sameScheme === null && item.tax_scheme && item.tax_scheme.rate !== 0) {
              sameScheme = item.tax_scheme.id
              tax_scheme = item.tax_scheme
            } else if (sameScheme === item.tax_scheme?.id || item.tax_scheme.rate === 0) {
              // do nothing
            } else {
              sameScheme = false
            }
          }
        })
        if (typeof sameScheme === 'number' && tax_scheme) {
          return {
            name: tax_scheme.friendly_name || '',
            rate: tax_scheme.rate || '',
          }
        } else {
          return { name: 'Tax', rate: '' }
        }
      } else {
        return { name: '', rate: '' }
      }
    })
    return {
      props,
      // columns,
      numberToText,
      formatNumberWithComma,
      tax,
      Decimal,
    }
  },
}
</script>

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
  <q-markup-table bordered flat>
    <thead>
      <q-tr class="text-left">
        <q-th data-testid="SN">
          SN
        </q-th>
        <q-th data-testid="hs-code">
          H.S. code
        </q-th>
        <q-th data-testid="Particular">
          Particular
        </q-th>
        <q-th data-testid="Qty">
          Qty
        </q-th>
        <q-th data-testid="Rate">
          Rate
        </q-th>
        <q-th data-testid="Discount">
          Discount
        </q-th>
        <q-th class="text-right" data-testid="Tax">
          Tax
        </q-th>
        <q-th class="text-right" data-testid="Amount">
          Amount
        </q-th>
      </q-tr>
    </thead>
    <tbody class="text-left">
      <q-tr v-for="(row, index) in fields?.rows" :key="index">
        <q-td>
          {{ index + 1 }}
        </q-td>
        <q-td>{{ row.hs_code }}</q-td>
        <q-td>
          {{ row.item_name }}
          <br />
          <span v-if="row.description" class="text-grey-8" style="font-size: 11px">
            <div v-for="(des, index) in row.description.split('\n')" :key="index" class="whitespace-normal">
              {{ des }}
            </div>
          </span>
        </q-td>
        <q-td>
          <template v-if="props.showRateQuantity">
            <FormattedNumber :value="row.quantity" />
            {{ ' ' }}
            <span class="text-grey-9">({{ row.unit_name }})</span>
          </template>
        </q-td>
        <q-td>
          <FormattedNumber v-if="props.showRateQuantity" type="currency" :value="row.rate" />
        </q-td>
        <q-td>
          <template v-if="row.discount_obj">
            <FormattedNumber v-if="row.discount_obj.type === 'Amount'" type="currency" :value="row.discount_obj.value" />
            <FormattedNumber
              v-else-if="row.discount_obj.type === 'Percent'"
              type="unit"
              unit="percent"
              :value="row.discount_obj.value"
            />
          </template>
          <template v-else-if="row.discount_type">
            <FormattedNumber v-if="row.discount_type === 'Amount'" type="currency" :value="row.discount" />
            <FormattedNumber
              v-else-if="row.discount_type === 'Percent'"
              type="unit"
              unit="percent"
              :value="row.discount"
            />
          </template>
        </q-td>
        <!-- <q-td> {{ row.discount }} </q-td> -->
        <q-td class="text-right">
          <FormattedNumber
            type="unit"
            unit="percent"
            :value="row.tax_scheme.rate"
          />
          {{ ' ' }}
          <span class="text-uppercase">({{ row.tax_scheme.friendly_name }})</span>
        </q-td>
        <q-td class="text-right">
          <FormattedNumber type="currency" :value="new Decimal(row.rate).mul(row.quantity).toNumber()" />
        </q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td class="text-right">
          Sub Total
        </q-td>
        <q-td class="text-right">
          <FormattedNumber type="currency" :value="fields?.voucher_meta.sub_total" />
        </q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td class="text-right">
          Discount
        </q-td>
        <q-td class="text-right">
          <FormattedNumber type="currency" :value="fields?.voucher_meta.discount" />
        </q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td class="text-right">
          {{ tax.name }}
          <template v-if="tax.rate">
            @ <FormattedNumber type="unit" unit="percent" :value="tax.rate" />
          </template>
        </q-td>
        <q-td class="text-right" data-testid="tax">
          <FormattedNumber type="currency" :value="fields?.voucher_meta.tax" />
        </q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td />
        <q-td class="text-right">
          Total
        </q-td>
        <q-td class="text-right">
          <FormattedNumber type="currency" :value="fields?.voucher_meta.grand_total" />
        </q-td>
      </q-tr>
      <q-tr class="text-subtitle2">
        <td></td>
        <td colspan="7">
          <span style="white-space: wrap">In Words: {{ numberToText(fields?.voucher_meta.grand_total) }}</span>
        </td>
      </q-tr>
    </tbody>
  </q-markup-table>
</template>
