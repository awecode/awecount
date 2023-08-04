<template>
  <div class="q-py-lg q-pl-lg q-mr-xl">
    <div class="row justify-between text-h4 text-bold">
      {{ fields?.name || '-' }}
      <q-btn v-if="checkPermissions('InventoryAccountView')" :to="`/items/details/${route.params.id}/`"
        color="orange-6">View Item</q-btn>
    </div>
    <div>
      <q-card class="q-mt-md">
        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Code</div>
                <div class="q-px-md">{{ fields?.code || '-' }}</div>
              </div>
              <hr />
            </div>
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Current Balance</div>
                <div class="q-px-md">{{ fields?.current_balance || '-' }}</div>
              </div>
              <hr />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Category</div>
                <div class="q-px-md">{{ fields?.category || '-' }}</div>
              </div>
              <hr />
            </div>
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Opening Balance</div>
                <div class="q-px-md">{{ fields?.opening_balance || '-' }}</div>
              </div>
              <hr />
            </div>
          </div>
          <div class="row q-col-gutter-md">
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Parent</div>
                <div class="q-px-md">{{ fields?.parent || '-' }}</div>
              </div>
            </div>
            <div class="col-6">
              <div class="row justify-between q-py-sm">
                <div class="q-px-md text-grey-8">Closing Balance</div>
                <div class="q-px-md">{{ (fields?.opening_balance || 0) - (fields?.current_balance || 0) }}</div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
      <div>
        <div class="text-h5 text-bold q-py-md">Transactions</div>
        <div class="row q-col-gutter-md">
          <DateRangePicker v-model:startDate="startDate" v-model:endDate="endDate" />
          <!-- <div v-if="startDate != null || endDate != null">
            <q-btn
              @click.prevent="resetDate"
              square
              color="red"
              icon="fa-solid fa-xmark"
              class="q-mt-md"
            />
          </div> -->
          <div>
            <q-btn @click.prevent="filter" color="primary" label="FILTER" class="q-mt-md" />
          </div>
        </div>
      </div>
      <q-table :columns="columnList" :rows="rows" :loading="loading" v-model:pagination="pagination" row-key="id"
        @request="onRequest" class="q-mt-lg" :binary-state-sort="true" :rows-per-page-options="[20]">
        <template v-slot:body-cell-voucher_no="props">
          <q-td :props="props">
            <router-link v-if="checkPermissions(getPermissionsWithSourceType[props.row.source_type])"
              :to="getVoucherUrl(props.row)" class="text-blue text-weight-medium" style="text-decoration: none">{{
                props.row.voucher_no }}</router-link>
            <span v-else>{{ props.row.voucher_no }}</span>
          </q-td>
        </template>
      </q-table>
    </div>
  </div>
</template>

<script setup>
import useApi from 'src/composables/useApi'
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
import checkPermissions from 'src/composables/checkPermissions';
const metaData = {
  title: 'Inventory Accounts Details | Awecount',
}
useMeta(metaData)
const store = useLoginStore()
const fields = ref(null)
const route = useRoute()
const startDate = ref(null)
const endDate = ref(null)
const filter = () => {
  endpoint.value = `/v1/inventory-account/${route.params.id}/transactions/?start_date=${startDate.value}&end_date=${endDate.value}`
  getData()
}

const endpoint = ref(`/v1/inventory-account/${route.params.id}/transactions/`)

const getData = () =>
  useApi(endpoint.value).then((data) => {
    fields.value = data
    loadData()
  })
getData()

const pagination = ref()
const loading = ref(false)
const initiallyLoaded = ref(false)
const rows = ref([])
const columnList = [
  {
    name: 'date',
    label: 'Date',
    align: 'left',
    field: (row) =>
      DateConverter.getRepresentation(
        row.date,
        store.isCalendarInAD ? 'ad' : 'bs'
      ),
  },
  {
    name: 'voucher_type',
    label: 'Voucher Type',
    align: 'left',
    field: 'source_type',
  },
  {
    name: 'voucher_no',
    label: 'Voucher No.',
    align: 'center',
    field: 'voucher_no',
  },
  {
    name: 'dr_amount',
    label: 'Dr',
    align: 'left',
    field: 'dr_amount',
  },
  {
    name: 'cr_amount',
    label: 'Cr',
    align: 'left',
    field: 'cr_amount',
  },
]

function loadData() {
  loading.value = true
  const field = fields.value.transactions.results.value
    ? Object.keys(fields.value?.transactions?.results[0])?.filter(
      (f) => f !== 'id'
    )
    : null

  // columnList.value = field?.map((f) => {
  //   return {
  //     name: f,
  //     label:
  //       f.replace(/_/g, ' ').charAt(0).toUpperCase() +
  //       f.replace(/_/g, ' ').slice(1),
  //     align: 'left',
  //     field: f,
  //   }
  // })

  rows.value = fields.value?.transactions?.results
  initiallyLoaded.value = true
  pagination.value = {
    page: fields.value?.transactions?.pagination?.page,
    rowsPerPage: fields.value?.transactions?.pagination?.size,
    rowsNumber: fields.value?.transactions?.pagination?.count,
  }

  loading.value = false
}

function onRequest(prop) {
  endpoint.value = `/v1/inventory-account/${route.params.id}/transactions/?${startDate.value && endDate.value
    ? 'start_date=' + startDate.value + '&end_date=' + endDate.value
    : ''
    }${startDate.value && endDate.value
      ? '&page=' + prop.pagination.page
      : 'page=' + prop.pagination.page
    }`
  getData()
}
// TODO: add permissions
function getVoucherUrl(row) {
  const source_type = row.source_type
  if (source_type === 'Sales Voucher')
    return `/sales-voucher/${row.source_id}/view/`
  if (source_type === 'Purchase Voucher')
    return `/purchase-voucher/${row.source_id}/view`
  if (source_type === 'Journal Voucher')
    return `/journal-voucher/${row.source_id}/view`
  if (source_type === 'Credit Note') return `/credit-note/${row.source_id}/view`
  if (source_type === 'Debit Note') return `/debit-note/${row.source_id}/view`
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
    return `/account/opening-balance/${row.source_id}/edit/`
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
  'Item': 'ItemView'
}
</script>
