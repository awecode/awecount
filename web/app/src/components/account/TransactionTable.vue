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
      <tr
        class="text-weight-bold"
        v-if="
          fields.aggregate &&
          fields.aggregate.total &&
          fields.aggregate.opening &&
          (fields.aggregate.opening.dr_amount__sum ||
            fields.aggregate.opening.cr_amount__sum)
        "
      >
        <td rowspan="1" colspan="2"></td>
        <td class="text-left">Opening</td>
        <td></td>
        <td class="text-left">
          {{
            Math.round((fields.aggregate.opening.dr_amount__sum || 0) * 100) /
            100
          }}
        </td>
        <td class="text-left">
          {{
            Math.round((fields.aggregate.opening.cr_amount__sum || 0) * 100) /
            100
          }}
        </td>
        <td>
          {{
            Math.round(
              ((fields.aggregate.opening.dr_amount__sum || 0) -
                (fields.aggregate.opening.cr_amount__sum || 0)) *
                100
            ) / 100
          }}
        </td>
      </tr>
      <tr
        class="text-weight-bold"
        v-if="
          fields.aggregate &&
          fields.aggregate.total &&
          (fields.aggregate.total.dr_amount__sum ||
            fields.aggregate.total.cr_amount__sum)
        "
      >
        <td colspan="2"></td>
        <td class="text-left">Transactions</td>
        <td></td>
        <td class="text-left">
          {{
            Math.round((fields.aggregate.total.dr_amount__sum || 0) * 100) / 100
          }}
        </td>
        <td class="text-left">
          {{
            Math.round((fields.aggregate.total.cr_amount__sum || 0) * 100) / 100
          }}
        </td>
        <td class="text-left">
          {{
            Math.round(
              ((fields.aggregate.total.dr_amount__sum || 0) -
                (fields.aggregate.total.cr_amount__sum || 0)) *
                100
            ) / 100
          }}
        </td>
      </tr>
      <tr
        class="text-weight-bold"
        v-if="
          fields.aggregate && fields.aggregate.total && fields.aggregate.opening
        "
      >
        <td colspan="2"></td>
        <td class="text-left">Closing</td>
        <td></td>
        <td class="text-left">
          {{
            Math.round(
              (fields.aggregate.opening.dr_amount__sum || 0) +
                (fields.aggregate.total.dr_amount__sum || 0) * 100
            ) / 100
          }}
        </td>
        <td class="text-left">
          {{
            Math.round(
              ((fields.aggregate.opening.cr_amount__sum || 0) +
                (fields.aggregate.total.cr_amount__sum || 0)) *
                100
            ) / 100
          }}
        </td>
        <td class="text-left">
          {{
            Math.round(
              ((fields.aggregate.opening.dr_amount__sum || 0) +
                (fields.aggregate.total.dr_amount__sum || 0) -
                ((fields.aggregate.opening.cr_amount__sum || 0) +
                  (fields.aggregate.total.cr_amount__sum || 0)) || 0) * 100
            ) / 100
          }}
        </td>
      </tr>
      <tr v-for="(transaction, index) in mergedTransactions" :key="index">
        <td>
          {{
            store.isCalendarInAD
              ? transaction.date
              : DateConverter.getRepresentation(transaction.date, 'bs')
          }}
        </td>
        <td>{{ transaction.source_type }}</td>
        <td>
          <div v-for="account in transaction.accounts" :key="account.id">
            <router-link
              v-if="account.id !== fields.id"
              :to="`/account/${account.id}/view/`"
              style="font-weight: 500; text-decoration: none"
              class="text-blue"
              :title="`${account.name}`"
            >
              {{ account.name }}
            </router-link>
          </div>
        </td>
        <td>
          <router-link
            v-if="
              checkPermissions(
                getPermissionsWithSourceType[transaction.source_type]
              ) && transaction.voucher_no
            "
            class="text-blue"
            style="text-decoration: none"
            :to="getVoucherUrl(transaction)"
            >{{ transaction.voucher_no }}</router-link
          >
          <span v-else> {{ transaction.voucher_no }} </span>
        </td>
        <td>
          <span v-if="transaction.dr_amount">{{
            Math.round((transaction.dr_amount || 0) * 100) / 100
          }}</span>
        </td>
        <td>
          <span v-if="transaction.cr_amount">{{
            Math.round((transaction.cr_amount || 0) * 100) / 100
          }}</span>
        </td>
        <td v-if="fields.aggregate"></td>
      </tr>

      <tr
        class="text-weight-bold"
        v-if="
          fields.aggregate &&
          fields.aggregate.total &&
          (fields.aggregate.total.dr_amount__sum ||
            fields.aggregate.total.cr_amount__sum)
        "
      >
        <td colspan="2"></td>
        <td class="text-left">Total</td>
        <td></td>
        <td class="text-left">
          {{
            Math.round((fields.aggregate.total.dr_amount__sum || 0) * 100) / 100
          }}
        </td>
        <td class="text-left">
          {{
            Math.round((fields.aggregate.total.cr_amount__sum || 0) * 100) / 100
          }}
        </td>
        <td>
          {{
            Math.round(
              ((fields.aggregate.total.dr_amount__sum || 0) -
                (fields.aggregate.total.cr_amount__sum || 0)) *
                100
            ) / 100
          }}
        </td>
      </tr>
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
    interface Amounts {
      dr: number
      cr: number
    }
    interface Fields {
      customer_account: Record<string, string | number | Amounts> | null
      name: string
      supplier_account: Record<string, string | number | Amounts> | null
    }
    const fields = ref(props.fields)
    watch(
      () => props.fields,
      (newValue) => {
        fields.value = newValue
      }
    )
    // function getEndPoint() {
    //   return `parties/${this.$route.params.pk}/transactions/`
    // }
    function getVoucherUrl(row) {
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
      Challan: 'ChallanModify',
      'Account Opening Balance': 'AccountOpeningBalanceModify',
      'Fund Transfer': 'FundTransferModify',
      'Bank Cash Deposit': 'BankCashDepositModify',
      'Tax Payment': 'TaxPaymentModify',
      Item: 'ItemView',
    }
    const mergedTransactions = computed(() => {
      let dct: Record<string, any> = {}
      if (fields.value?.transactions?.results) {
        fields.value.transactions.results.forEach((transaction) => {
          const sourceType = transaction.source_type
            .toLowerCase()
            .replace(' ', '')
          const key = `${sourceType}-${123}`
          if (key in dct && dct[key].date === transaction.date) {
            dct[key].accounts.push('agvsghvasgcvag')
            if (transaction.dr_amount) {
              dct[key].dr_amount =
                parseFloat(transaction.dr_amount) +
                parseFloat(dct[key].dr_amount)
            }
            if (transaction.cr_amount) {
              dct[key].cr_amount =
                parseFloat(transaction.cr_amount) +
                parseFloat(dct[key].cr_amount)
            }
          } else {
            dct[key] = transaction
          }
        })
      }

      return Object.keys(dct).map(function (key) {
        return dct[key]
      })
    })
    return {
      props,
      getVoucherUrl,
      checkPermissions,
      getPermissionsWithSourceType,
      store,
      DateConverter,
      mergedTransactions,
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
