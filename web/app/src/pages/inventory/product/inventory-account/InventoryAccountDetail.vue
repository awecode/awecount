<script setup>
import DateConverter from 'src/components/date/VikramSamvat.js'
import checkPermissions from 'src/composables/checkPermissions'
import useApi from 'src/composables/useApi'
import { useLoginStore } from 'src/stores/login-info'

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
  endpoint.value = `/api/company/${route.params.company}/inventory-account/${route.params.id}/transactions/?start_date=${startDate.value}&end_date=${endDate.value}`
  getData()
}

const endpoint = ref(`/api/company/${route.params.company}/inventory-account/${route.params.id}/transactions/`)

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
    field: (row) => DateConverter.getRepresentation(row.date, store.isCalendarInAD ? 'ad' : 'bs'),
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
  // const field = fields.value.transactions.results.value
  //   ? Object.keys(fields.value?.transactions?.results[0])?.filter(
  //     (f) => f !== 'id'
  //   )
  //   : null

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
  endpoint.value = `/api/company/${route.params.company}/inventory-account/${route.params.id}/transactions/?${startDate.value && endDate.value ? `start_date=${startDate.value}&end_date=${endDate.value}` : ''}${startDate.value && endDate.value ? `&page=${prop.pagination.page}` : `page=${prop.pagination.page}`}`
  getData()
}
// TODO: add permissions
function getVoucherUrl(row) {
  const source_type = row.source_type
  if (source_type === 'Sales Voucher') {
    return `/${route.params.company}/sales-voucher/${row.source_id}/view/`
  }
  if (source_type === 'Purchase Voucher') {
    return `/${route.params.company}/purchase-voucher/${row.source_id}/view`
  }
  if (source_type === 'Journal Voucher') {
    return `/${route.params.company}/journal-voucher/${row.source_id}/view`
  }
  if (source_type === 'Credit Note') return `/${route.params.company}/credit-note/${row.source_id}/view`
  if (source_type === 'Debit Note') return `/${route.params.company}/debit-note/${row.source_id}/view`
  // if (source_type === 'Tax Payment') return 'Tax Payment Edit'
  // TODO: add missing links
  if (source_type === 'Cheque Deposit') {
    return `/${route.params.company}/cheque-deposit/${row.source_id}/view/`
  }
  if (source_type === 'Payment Receipt') {
    return `/${route.params.company}/payment-receipt/${row.source_id}/view/`
  }
  if (source_type === 'Cheque Issue') {
    return `/${route.params.company}/cheque-issue/${row.source_id}/`
  }
  if (source_type === 'Challan') return `/${route.params.company}/challan/${row.source_id}/`
  if (source_type === 'Account Opening Balance') {
    return `/${route.params.company}/account/opening-balance/${row.source_id}/edit/`
  }
  if (source_type === 'Item') return `/${route.params.company}/items/${row.source_id}/`
  // added
  if (source_type === 'Fund Transfer') {
    return `/${route.params.company}/bank/fund/fund-transfer/${row.source_id}/edit/`
  }
  if (source_type === 'Bank Cash Deposit') {
    return `/${route.params.company}/bank/cash/cash-deposit/${row.source_id}/edit/`
  }
  if (source_type === 'Tax Payment') return `/${route.params.company}/tax-payment/${row.source_id}/`
  if (source_type === 'Inventory Adjustment Voucher') return `/${route.params.company}/items/inventory-adjustment/${row.source_id}/view/`
  if (source_type === 'Inventory Conversion Voucher') return `/${route.params.company}/items/inventory-conversion/${row.source_id}/view/`
  console.error(`${source_type} not handled!`)
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
  'Inventory Adjustment Voucher': 'InventoryAdjustmentVoucherView',
  'Inventory Conversion Voucher': 'InventoryConversionVoucherView',
}
</script>

<template>
  <div class="q-py-lg q-pl-lg q-mr-xl">
    <div class="flex justify-between">
      <div class="text-h5">
        <router-link v-if="checkPermissions('inventoryaccount.view')" :to="`/${$route.params.company}/items/${fields?.item}/`" style="font-weight: 500; text-decoration: none" class="text-blue">
          {{ fields?.name }}
        </router-link>
        <span v-else class="text-bold">{{ fields?.name || '-' }}</span>
        <span v-if="fields?.category_name" class="q-ml-md text-h6 text-grey-7">
          ({{ fields?.category_name || '-' }})
          <q-tooltip>Category</q-tooltip>
        </span>
      </div>
      <div>
        <span v-if="fields?.code" class="ml-2 text-h6 text-grey-9 text-sm p-2 -mb-2 inline-block">[Code: {{ fields.code }}]</span>
      </div>
    </div>
    <div class="mt-8">
      <div class="grid lg:grid-cols-3 gap-x-6 gap-y-1">
        <div class="row justify-between q-py-sm b">
          <div class="q-px-md text-grey-8">Current Balance</div>
          <div class="q-px-md">
            {{ $nf(fields?.current_balance) || '-' }}
          </div>
        </div>

        <div class="row justify-between q-py-sm b">
          <div class="q-px-md text-grey-8">Opening Balance</div>
          <div class="q-px-md">
            {{ $nf(fields?.opening_balance) || '-' }}
          </div>
        </div>

        <div class="row justify-between q-py-sm b">
          <div class="q-px-md text-grey-8">Closing Balance</div>
          <div class="q-px-md">
            {{ $nf(fields?.closing_balance) || '-' }}
          </div>
        </div>
      </div>
      <div class="mt-8 px-2">
        <div class="flex gap-x-2 mb-4 items-center">
          <DateRangePicker v-model:start-date="startDate" v-model:end-date="endDate" />
          <div>
            <q-btn color="primary" label="FILTER" :disabled="!(startDate && endDate)" @click.prevent="filter" />
          </div>
        </div>
      </div>
      <q-table v-model:pagination="pagination" :columns="columnList" :rows="rows" :loading="loading" row-key="id" class="q-mt-xs" :binary-state-sort="true" :rows-per-page-options="[20]" @request="onRequest">
        <template #body-cell-voucher_no="props">
          <q-td :props="props">
            <router-link v-if="checkPermissions(getPermissionsWithSourceType[props.row.source_type])" :to="getVoucherUrl(props.row)" class="text-blue text-weight-medium" style="text-decoration: none">
              {{ props.row.voucher_no }}
            </router-link>
            <span v-else>{{ props.row.voucher_no }}</span>
          </q-td>
        </template>

        <template #body-cell-voucher_type="props">
          <q-td :props="props">
            <span>{{ props.row.source_type === 'Item' ? 'Opening' : props.row.source_type }}</span>
          </q-td>
        </template>
      </q-table>
    </div>
  </div>
</template>
