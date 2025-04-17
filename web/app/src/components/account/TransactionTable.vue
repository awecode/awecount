<script lang="ts">
import type { Ref } from 'vue'

import Decimal from 'decimal.js'
import DateConverter from 'src/components/date/VikramSamvat.js'
import checkPermissions from 'src/composables/checkPermissions'
import { useLoginStore } from 'src/stores/login-info'

export default {
  props: {
    fields: {
      type: Object || null,
      default: null,
    },
  },
  setup(props) {
    const store = useLoginStore()
    const route = useRoute()

    const fields: Ref<null | Record<string, any>> = ref(props.fields)
    watch(
      () => props.fields,
      (newValue) => {
        fields.value = newValue
      },
    )
    function getVoucherUrl(row) {
      const source_type = row.source_type
      if (source_type === 'Sales Voucher') {
        return `/${route.params.company}/sales/vouchers/${row.source_id}`
      }
      if (source_type === 'Purchase Voucher') {
        return `/${route.params.company}/purchase/vouchers/${row.source_id}`
      }
      if (source_type === 'Journal Voucher') {
        return `/${route.params.company}/account/journal-vouchers/${row.source_id}`
      }
      if (source_type === 'Credit Note') {
        return `/${route.params.company}/sales/credit-notes/${row.source_id}`
      }
      if (source_type === 'Debit Note') {
        return `/${route.params.company}/purchase/debit-notes/${row.source_id}`
      }
      if (source_type === 'Challan') {
        return `/${route.params.company}/sales/challans/${row.source_id}`
      }
      if (source_type === 'Cheque Deposit') {
        return `/${route.params.company}/banking/cheque-deposit/${row.source_id}`
      }
      if (source_type === 'Payment Receipt') {
        return `/${route.params.company}/payment-receipts/${row.source_id}`
      }
      if (source_type === 'Cheque Issue') {
        return `/${route.params.company}/banking/cheque-issue/${row.source_id}/edit`
      }
      if (source_type === 'Account Opening Balance') {
        return `/${route.params.company}/account/opening-balances/${row.source_id}/edit`
      }
      if (source_type === 'Fund Transfer') {
        return `/${route.params.company}/banking/fund-transfers/${row.source_id}/edit`
      }
      if (source_type === 'Bank Cash Deposit') {
        return `/${route.params.company}/banking/cash-deposit/${row.source_id}/edit`
      }
      if (source_type === 'Tax Payment') {
        return `/${route.params.company}/tax/payments/${row.source_id}/edit`
      }
      if (source_type === 'Inventory Adjustment Voucher') {
        return `/${route.params.company}/inventory/adjustments/${row.source_id}`
      }
      console.error(`${source_type} not handled!`)
    }
    const getPermissionsWithSourceType = {
      'Account Opening Balance': 'accountopeningbalance.update',
      'Bank Cash Deposit': 'bankcashdeposit.update',
      'Challan': 'challan.update',
      'Cheque Deposit': 'chequedeposit.read',
      'Cheque Issue': 'chequeissue.update',
      'Credit Note': 'creditnote.read',
      'Debit Note': 'debitnote.read',
      'Fund Transfer': 'fundtransfer.update',
      'Inventory Adjustment Voucher': 'inventoryadjustmentvoucher.read',
      'Item': 'item.read',
      'Journal Voucher': 'journalvoucher.read',
      'Payment Receipt': 'paymentreceipt.read',
      'Purchase Voucher': 'purchasevoucher.read',
      'Sales Voucher': 'sales.read',
      'Tax Payment': 'taxpayment.update',
    }
    const runningBalance = computed(() => {
      const runningBalanceData: Record<number, Record<string, number | string | null>> = {}
      if (fields.value?.transactions?.results && fields.value.page_cumulative) {
        const openingBalance = { dr: 0, cr: 0 }
        if (route.query.start_date) {
          openingBalance.dr = (fields.value.aggregate.opening.dr || 0) + (fields.value.page_cumulative.next.dr || 0)
          openingBalance.cr = (fields.value.aggregate.opening.cr || 0) + (fields.value.page_cumulative.next.cr || 0)
        } else {
          openingBalance.dr = fields.value.page_cumulative.next.dr || 0
          openingBalance.cr = fields.value.page_cumulative.next.cr || 0
        }
        let currentRunningBalance = openingBalance
        const reversedTransactions = [...fields.value.transactions.results].reverse()
        const dataLength = fields.value.transactions.results.length - 1
        reversedTransactions.forEach((item, index) => {
          const activeBalance = { ...currentRunningBalance }
          activeBalance.dr = activeBalance.dr + (item.dr_amount ? Number.parseFloat(item.dr_amount) : 0)
          activeBalance.cr = activeBalance.cr + (item.cr_amount ? Number.parseFloat(item.cr_amount) : 0)
          const dataIndex = dataLength - index
          runningBalanceData[dataIndex] = activeBalance
          currentRunningBalance = activeBalance
        })
      }
      return runningBalanceData
    })
    return {
      props,
      getVoucherUrl,
      Decimal,
      checkPermissions,
      getPermissionsWithSourceType,
      store,
      DateConverter,
      runningBalance,
    }
  },
}
</script>

<template>
  <q-markup-table v-if="fields" class="box-shadow q-mt-sm">
    <!-- TODO: aggregate data not availaible, so check if it works -->
    <thead>
      <tr>
        <th class="text-left">
          Date
        </th>
        <th class="text-left">
          Voucher Type
        </th>
        <th class="text-left">
          Against
        </th>
        <th class="text-left">
          Voucher No.
        </th>
        <th class="text-left">
          Dr
        </th>
        <th class="text-left">
          Cr
        </th>
        <th v-if="fields.aggregate" class="text-left">
          Balance
        </th>
      </tr>
    </thead>
    <tbody v-if="fields.transactions">
      <!-- <tr class="text-weight-bold" v-if="fields.aggregate &&
        fields.aggregate.total &&
        (fields.aggregate.total.dr_amount__sum ||
          fields.aggregate.total.cr_amount__sum)
        ">
        <td colspan="2"></td>
        <td class="text-left">Transactions</td>
        <td></td>
        <td class="text-left">
          {{ $nf(fields.aggregate.total.dr_amount__sum, 2) }}
        </td>
        <td class="text-left">
          {{ $nf(fields.aggregate.total.cr_amount__sum, 2) }}
        </td>
        <td class="text-left">
          {{ $nf((fields.aggregate.total.dr_amount__sum || 0) - (fields.aggregate.total.cr_amount__sum || 0), 2) }}
        </td>
      </tr> -->
      <!-- <tr class="text-weight-bold">
        <td colspan="2"></td>
        <td class="text-left">Final Opening</td>
        <td></td>
        <td class="text-left">
          {{
            $nf(
              fields.page_cumulative.current.dr +
                fields.page_cumulative.next.dr +
                ($route.query.start_date
                  ? fields.aggregate.opening.dr || 0
                  : 0),
              2
            )
          }}
        </td>
        <td class="text-left">
          {{ $nf(fields.amounts.cr || 0) }}
        </td>
        <td class="text-left">
          {{ $nf((fields.amounts.dr || 0) - (fields.amounts.cr || 0), 2) }}
        </td>
      </tr> -->
      <template v-if="fields.amounts">
        <tr v-if="$route.query.end_date" class="text-weight-bold">
          <td colspan="2"></td>
          <td class="text-left">
            Final Closing
          </td>
          <td></td>
          <td class="text-left">
            <FormattedNumber type="currency" :value="new Decimal(fields.aggregate.total.dr).add(fields.aggregate.opening.dr).toNumber()" />
          </td>
          <td class="text-left">
            <FormattedNumber type="currency" :value="new Decimal(fields.aggregate.total.cr).add(fields.aggregate.opening.cr).toNumber()" />
          </td>
          <td class="text-left">
            <FormattedNumber type="currency" :value="new Decimal(fields.aggregate.total.dr).add(fields.aggregate.opening.dr).sub(fields.aggregate.total.cr).sub(fields.aggregate.opening.cr).toNumber()" />
          </td>
        </tr>
        <tr v-else class="text-weight-bold">
          <td colspan="2"></td>
          <td class="text-left">
            Final Closing
          </td>
          <td></td>
          <td class="text-left">
            <FormattedNumber type="currency" :value="fields.amounts.dr ?? '0'" />
          </td>
          <td class="text-left">
            <FormattedNumber type="currency" :value="fields.amounts.cr ?? '0'" />
          </td>
          <td class="text-left">
            <FormattedNumber type="currency" :value="new Decimal(fields.amounts.dr ?? '0').sub(fields.amounts.cr ?? '0').toNumber()" />
          </td>
        </tr>
      </template>
      <tr v-if="$route.query.start_date && fields.page_cumulative" class="text-weight-bold">
        <td colspan="2"></td>
        <td class="text-left">
          Closing
        </td>
        <td></td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="new Decimal(fields.page_cumulative.current.dr).add(fields.page_cumulative.next.dr).add(fields.aggregate.opening.dr).toNumber()" />
        </td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="new Decimal(fields.page_cumulative.current.cr).add(fields.page_cumulative.next.cr).add(fields.aggregate.opening.cr).toNumber()" />
        </td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="new Decimal(fields.page_cumulative.current.dr).add(fields.page_cumulative.next.dr).add(fields.aggregate.opening.dr).sub(fields.page_cumulative.current.cr).sub(fields.page_cumulative.next.cr).sub(fields.aggregate.opening.cr).toNumber()" />
        </td>
      </tr>
      <tr v-else-if="fields.page_cumulative" class="text-weight-bold">
        <td colspan="2"></td>
        <td class="text-left">
          Closing
        </td>
        <td></td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="new Decimal(fields.page_cumulative.current.dr).add(fields.page_cumulative.next.dr).toNumber()" />
        </td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="new Decimal(fields.page_cumulative.current.cr).add(fields.page_cumulative.next.cr).toNumber()" />
        </td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="new Decimal(fields.page_cumulative.current.dr).add(fields.page_cumulative.next.dr).sub(fields.page_cumulative.current.cr).sub(fields.page_cumulative.next.cr).toNumber()" />
        </td>
      </tr>
      <tr v-for="(transaction, index) in fields.transactions.results" :key="index">
        <td>
          {{ store.isCalendarInAD ? transaction.date : DateConverter.getRepresentation(transaction.date, 'bs') }}
        </td>
        <td>{{ transaction.source_type }}</td>
        <td>
          <account-list :accounts="transaction.accounts" />
          <!-- <div v-for="(id, index) in transaction.account_ids" :key="id">
            <router-link :to="`/${$route.params.company}/account/ledgers/${id}`"
              style="font-weight: 500; text-decoration: none" class="text-blue" :title="`${transaction.account_names}`">
              {{ account.name }}
            </router-link>
          </div> -->
        </td>
        <td>
          <router-link
            v-if="transaction.source_type && transaction.voucher_no && checkPermissions(getPermissionsWithSourceType[transaction.source_type])"
            class="text-blue"
            style="text-decoration: none"
            :to="getVoucherUrl(transaction)"
          >
            {{ transaction.voucher_no }}
          </router-link>
          <span v-else>{{ transaction.voucher_no }}</span>
        </td>
        <td>
          <FormattedNumber type="currency" :value="transaction.dr_amount" />
        </td>
        <td>
          <FormattedNumber type="currency" :value="transaction.cr_amount" />
        </td>
        <td v-if="runningBalance && Object.keys(runningBalance).length">
          <FormattedNumber type="currency" :value="new Decimal(runningBalance[index].dr).sub(runningBalance[index].cr).toNumber()" />
        </td>
      </tr>

      <tr v-if="fields.aggregate && fields.aggregate.total && (fields.aggregate.total.dr_amount__sum || fields.aggregate.total.cr_amount__sum)" class="text-weight-bold">
        <td colspan="2"></td>
        <td class="text-left">
          Total
        </td>
        <td></td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="fields.aggregate.total.dr_amount__sum" />
        </td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="fields.aggregate.total.cr_amount__sum" />
        </td>
        <td>
          <FormattedNumber type="currency" :value="new Decimal(fields.aggregate.total.dr_amount__sum ?? '0').sub(fields.aggregate.total.cr_amount__sum ?? '0').toNumber()" />
        </td>
      </tr>

      <!-- <template v-if="Object.keys(fields.aggregate).length">
        <tr class="text-weight-bold">
          <td rowspan="1" colspan="2"></td>
          <td class="text-left">Opening</td>
          <td></td>
          <td class="text-left">
            {{ $nf(fields.aggregate.opening.dr_amount, 2) }}
          </td>
          <td class="text-left">
            {{ $nf(fields.aggregate.opening.cr_amount, 2) }}
          </td>
          <td>
            {{
              $nf(
                (fields.aggregate.opening.dr_amount || 0) -
                  (fields.aggregate.opening.cr_amount || 0),
                2
              )
            }}
          </td>
        </tr>
      </template> -->

      <tr v-if="$route.query.start_date" class="text-weight-bold">
        <td colspan="2" rowspan="1"></td>
        <td class="text-left">
          Opening
        </td>
        <td></td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="new Decimal(fields.aggregate.opening.dr).add(fields.page_cumulative.next.dr).toNumber()" />
        </td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="new Decimal(fields.aggregate.opening.cr).add(fields.page_cumulative.next.cr).toNumber()" />
        </td>
        <td>
          <FormattedNumber type="currency" :value="new Decimal(fields.aggregate.opening.dr).add(fields.page_cumulative.next.dr).sub(fields.aggregate.opening.cr).sub(fields.page_cumulative.next.cr).toNumber()" />
        </td>
      </tr>
      <tr v-else-if="fields.page_cumulative" class="text-weight-bold">
        <td colspan="2" rowspan="1"></td>
        <td class="text-left">
          Opening
        </td>
        <td></td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="fields.page_cumulative.next.dr" />
        </td>
        <td class="text-left">
          <FormattedNumber type="currency" :value="fields.page_cumulative.next.cr" />
        </td>
        <td>
          <FormattedNumber type="currency" :value="new Decimal(fields.page_cumulative.next.dr).sub(fields.page_cumulative.next.cr).toNumber()" />
        </td>
      </tr>
      <!-- <tr class="text-weight-bold">
        <td colspan="2"></td>
        <td class="text-left">Initial Opening</td>
        <td></td>
        <td class="text-left">
          {{
            $nf(
              $route.query.start_date ? fields.aggregate.opening.dr || 0 : 0,
              2
            )
          }}
        </td>
        <td class="text-left">
          {{
            $nf(
              $route.query.start_date ? fields.aggregate.opening.cr || 0 : 0,
              2
            )
          }}
        </td>
        <td class="text-left">
          {{
            $nf(
              $route.query.start_date
                ? (fields.aggregate.opening.dr || 0) -
                    (fields.aggregate.opening.cr || 0)
                : 0,
              2
            )
          }}
        </td>
      </tr> -->

      <tr>
        <td colspan="7">
          <slot></slot>
        </td>
      </tr>
    </tbody>
  </q-markup-table>
</template>

<style scoped>
.box-shadow {
  box-shadow:
    0 1px 5px rgba(0, 0, 0, 0.2),
    0 2px 2px rgba(0, 0, 0, 0.14),
    0 3px 1px -2px rgba(0, 0, 0, 0.12);
}

@media print {
  .box-shadow {
    box-shadow: none;
  }

  td,
  th {
    padding: 5px;
    margin: 0;
    font-size: 12px !important;
    height: inherit !important;
  }

  .q-card,
  .q-card__section {
    box-shadow: none !important;
  }
}
</style>
