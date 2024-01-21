<template>
  <q-markup-table class="box-shadow q-mt-sm" v-if="fields">
    <!-- TODO: aggregate data not availaible, so check if it works -->
    <thead>
      <tr>
        <th class="text-left">Date</th>
        <th class="text-left">Voucher Type</th>
        <th class="text-left">Against</th>
        <th class="text-left">Voucher No.</th>
        <th class="text-left">Dr</th>
        <th class="text-left">Cr</th>
        <th v-if="fields.aggregate" class="text-left">Balance</th>
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
        <tr class="text-weight-bold" v-if="$route.query.end_date">
          <td colspan="2"></td>
          <td class="text-left">Final Closing</td>
          <td></td>
          <td class="text-left">
            {{
              $nf(fields.aggregate.total.dr + fields.aggregate.opening.dr, 2)
            }}
          </td>
          <td class="text-left">
            {{
              $nf(fields.aggregate.total.cr + fields.aggregate.opening.cr, 2)
            }}
          </td>
          <td class="text-left">
            {{
              $nf(
                fields.aggregate.total.dr +
                fields.aggregate.opening.dr -
                (fields.aggregate.total.cr + fields.aggregate.opening.cr),
                2
              )
            }}
          </td>
        </tr>
        <tr class="text-weight-bold" v-else>
          <td colspan="2"></td>
          <td class="text-left">Final Closing</td>
          <td></td>
          <td class="text-left">
            {{ $nf(fields.amounts.dr || 0, 2) }}
          </td>
          <td class="text-left">
            {{ $nf(fields.amounts.cr || 0, 2) }}
          </td>
          <td class="text-left">
            {{ $nf((fields.amounts.dr || 0) - (fields.amounts.cr || 0), 2) }}
          </td>
        </tr>
      </template>
      <tr class="text-weight-bold" v-if="$route.query.start_date">
        <td colspan="2"></td>
        <td class="text-left">Closing</td>
        <td></td>
        <td class="text-left">
          {{
            $nf(
              fields.page_cumulative.current.dr +
              fields.page_cumulative.next.dr +
              fields.aggregate.opening.dr,
              2
            )
          }}
        </td>
        <td class="text-left">
          {{
            $nf(
              fields.page_cumulative.current.cr +
              fields.page_cumulative.next.cr +
              fields.aggregate.opening.cr,
              2
            )
          }}
        </td>
        <td class="text-left">
          {{
            $nf(
              fields.page_cumulative.current.dr +
              fields.page_cumulative.next.dr +
              fields.aggregate.opening.dr -
              (fields.page_cumulative.current.cr +
                fields.page_cumulative.next.cr +
                fields.aggregate.opening.cr),
              2
            )
          }}
        </td>
      </tr>
      <tr class="text-weight-bold" v-else>
        <td colspan="2"></td>
        <td class="text-left">Closing</td>
        <td></td>
        <td class="text-left">
          {{
            $nf(
              fields.page_cumulative.current.dr +
              fields.page_cumulative.next.dr,
              2
            )
          }}
        </td>
        <td class="text-left">
          {{
            $nf(
              fields.page_cumulative.current.cr +
              fields.page_cumulative.next.cr,
              2
            )
          }}
        </td>
        <td class="text-left">
          {{
            $nf(
              fields.page_cumulative.current.dr +
              fields.page_cumulative.next.dr -
              (fields.page_cumulative.current.cr +
                fields.page_cumulative.next.cr),
              2
            )
          }}
        </td>
      </tr>
      <tr v-for="(transaction, index) in fields.transactions.results" :key="index">
        <td>
          {{
            store.isCalendarInAD
            ? transaction.date
            : DateConverter.getRepresentation(transaction.date, 'bs')
          }}
        </td>
        <td>{{ transaction.source_type }}</td>
        <td>
          <account-list :accounts="transaction.accounts"></account-list>
          <!-- <div v-for="(id, index) in transaction.account_ids" :key="id">
            <router-link :to="`/account/${id}/view/`"
              style="font-weight: 500; text-decoration: none" class="text-blue" :title="`${transaction.account_names}`">
              {{ account.name }}
            </router-link>
          </div> -->
        </td>
        <td>
          <router-link v-if="transaction.source_type && transaction.voucher_no && checkPermissions(
            getPermissionsWithSourceType[transaction.source_type]
          )
            " class="text-blue" style="text-decoration: none" :to="getVoucherUrl(transaction)">{{
    transaction.voucher_no }}</router-link>
          <span v-else> {{ transaction.voucher_no }} </span>
        </td>
        <td>
          <span v-if="transaction.dr_amount">{{
            $nf(transaction.dr_amount, 2)
          }}</span>
        </td>
        <td>
          <span v-if="transaction.cr_amount">{{
            $nf(transaction.cr_amount, 2)
          }}</span>
        </td>
        <td v-if="runningBalance && Object.keys(runningBalance).length">
          {{ $nf((runningBalance[index].dr - runningBalance[index].cr), 2) }}
        </td>
      </tr>

      <tr class="text-weight-bold" v-if="fields.aggregate &&
        fields.aggregate.total &&
        (fields.aggregate.total.dr_amount__sum ||
          fields.aggregate.total.cr_amount__sum)
        ">
        <td colspan="2"></td>
        <td class="text-left">Total</td>
        <td></td>
        <td class="text-left">
          {{ $nf(fields.aggregate.total.dr_amount__sum, 2) }}
        </td>
        <td class="text-left">
          {{ $nf(fields.aggregate.total.cr_amount__sum, 2) }}
        </td>
        <td>
          {{
            $nf(
              (fields.aggregate.total.dr_amount__sum || 0) -
              (fields.aggregate.total.cr_amount__sum || 0),
              2
            )
          }}
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

      <tr class="text-weight-bold" v-if="$route.query.start_date">
        <td rowspan="1" colspan="2"></td>
        <td class="text-left">Opening</td>
        <td></td>
        <td class="text-left">
          {{
            $nf(fields.aggregate.opening.dr + fields.page_cumulative.next.dr, 2)
          }}
        </td>
        <td class="text-left">
          {{
            $nf(fields.aggregate.opening.cr + fields.page_cumulative.next.cr, 2)
          }}
        </td>
        <td>
          {{
            $nf(
              fields.aggregate.opening.dr +
              fields.page_cumulative.next.dr -
              (fields.aggregate.opening.cr + fields.page_cumulative.next.cr),
              2
            )
          }}
        </td>
      </tr>
      <tr class="text-weight-bold" v-else>
        <td rowspan="1" colspan="2"></td>
        <td class="text-left">Opening</td>
        <td></td>
        <td class="text-left">
          {{ $nf(fields.page_cumulative.next.dr, 2) }}
        </td>
        <td class="text-left">
          {{ $nf(fields.page_cumulative.next.cr, 2) }}
        </td>
        <td>
          {{
            $nf(
              fields.page_cumulative.next.dr - fields.page_cumulative.next.cr,
              2
            )
          }}
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
          <slot> </slot>
        </td>
      </tr>
    </tbody>
  </q-markup-table>
</template>

<script lang="ts">
import { Ref } from 'vue'
import checkPermissions from 'src/composables/checkPermissions'
import DateConverter from '/src/components/date/VikramSamvat.js'
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
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const fields: Ref<null | Record<string, any>> = ref(props.fields)
    watch(
      () => props.fields,
      (newValue) => {
        fields.value = newValue
      }
    )
    function getVoucherUrl(row: Record<string, string>) {
      if (!row.source_id) return ''
      const source_type = row.source_type
      if (source_type === 'Sales Voucher')
        return `/sales-voucher/${row.source_id}/view/`
      if (source_type === 'Purchase Voucher')
        return `/purchase-voucher/${row.source_id}/view`
      if (source_type === 'Journal Voucher')
        return `/journal-voucher/${row.source_id}/view`
      if (source_type === 'Credit Note')
        return `/credit-note/${row.source_id}/view`
      if (source_type === 'Debit Note')
        return `/debit-note/${row.source_id}/view`
      // if (source_type === 'Tax Payment') return 'Tax Payment Edit'
      // TODO: add missing links
      if (source_type === 'Cheque Deposit')
        return `/cheque-deposit/${row.source_id}/view/`
      if (source_type === 'Payment Receipt')
        return `/payment-receipt/${row.source_id}/view/`
      if (source_type === 'Cheque Issue')
        return `/cheque-issue/${row.source_id}/`
      if (source_type === 'Challan') return `/challan/${row.source_id}/`
      if (source_type === 'Account Opening Balance')
        return `/account-opening-balance/${row.source_id}/`
      if (source_type === 'Item') return `/items/details/${row.source_id}/`
      // added
      if (source_type === 'Fund Transfer')
        return `/bank/fund/fund-transfer/${row.source_id}/edit/`
      if (source_type === 'Bank Cash Deposit')
        return `/bank/cash/cash-deposit/${row.source_id}/edit/`
      if (source_type === 'Tax Payment') return `/tax-payment/${row.source_id}/`
      console.error(source_type + ' not handled!')
    }
    const getPermissionsWithSourceType = {
      'Sales Voucher': 'SalesView',
      'Purchase Voucher': 'PurchaseVoucherView',
      'Journal Voucher': 'JournalVoucherView',
      'Credit Note': 'CreditNoteView',
      'Debit Note': 'DebitNoteView',
      'Cheque Deposit': 'ChequeDepositView',
      'Payment Receipt': 'PaymentReceiptView',
      'Cheque Issue': 'ChequeIssueModify',
      'Challan': 'ChallanModify',
      'Account Opening Balance': 'AccountOpeningBalanceModify',
      'Fund Transfer': 'FundTransferModify',
      'Bank Cash Deposit': 'BankCashDepositModify',
      'Tax Payment': 'TaxPaymentModify',
      'Item': 'ItemView',
    }
    const runningBalance = computed(() => {
      const runningBalanceData: Record<
        number,
        Record<string, number | string | null>
      > = {}
      if (fields.value?.transactions?.results) {
        const openingBalance = { dr: 0, cr: 0 }
        if (route.query.start_date) {
          openingBalance.dr = (fields.value.aggregate.opening.dr || 0) + (fields.value.page_cumulative.next.dr || 0)
          openingBalance.cr = (fields.value.aggregate.opening.cr || 0) + (fields.value.page_cumulative.next.cr || 0)
        } else {
          openingBalance.dr = (fields.value.page_cumulative.next.dr || 0)
          openingBalance.cr = (fields.value.page_cumulative.next.cr || 0)
        }
        let currentRunningBalance = openingBalance
        const reversedTransactions = [...fields.value.transactions.results].reverse()
        const dataLength = fields.value.transactions.results.length - 1
        reversedTransactions.forEach((item, index) => {
          const activeBalance = { ...currentRunningBalance }
          activeBalance.dr =
            activeBalance.dr + (item.dr_amount ? parseFloat(item.dr_amount) : 0)
          activeBalance.cr =
            activeBalance.cr + (item.cr_amount ? parseFloat(item.cr_amount) : 0)
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
      checkPermissions,
      getPermissionsWithSourceType,
      store,
      DateConverter,
      runningBalance,
    }
  },
}
</script>

<style scoped>
.box-shadow {
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.2), 0 2px 2px rgba(0, 0, 0, 0.14),
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
