<template>
  <div class="q-pa-md">
    <div class="row justify-end">
      <q-btn color="blue" to="/bank-reconciliation/reconcile/" label="Manual Reconciliation" class="mr-5" />
      <q-btn v-if="checkPermissions('ReconciliationStatementCreate')" icon="mdi-file-upload-outline" color="green" label="Upload Statement" @click="statementPrompt = true"></q-btn>
    </div>

    <q-table :rows="rows" :columns="columns" :loading="loading" :filter="searchQuery" v-model:pagination="pagination" row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <div class="search-bar">
          <q-input dense debounce="500" v-model="searchQuery as string" placeholder="Search" class="full-width search-input">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="f-open-btn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(500px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <!-- <div class="q-ma-sm">
                    <MultiSelectChip :options="['Reconciled', 'Unreconciled']" v-model="filters.status" />
                  </div> -->
                  <div class="q-mx-md">
                    <!-- <DateRangePicker v-model:startDate="filters.start_date" v-model:endDate="filters.end_date" /> -->
                    <n-auto-complete v-model="filters.account_id" :options="bankAccounts" label="Bank Accounts" optionValue="ledger_id" />

                  </div>
                </div>
                <div class="q-mx-md flex gap-4 q-mb-md">
                  <q-btn color="green" label="Filter" @click="onFilterUpdate" class="f-submit-btn"></q-btn>
                  <q-btn color="red" icon="close" @click="resetFilters" class="f-reset-btn"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn v-if="checkPermissions('ReconciliationStatementView')" color="blue" class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn" style="font-size: 12px" label="View"
            :to="`/bank-reconciliation/${props.row.id}/`" />
          <q-btn v-if="checkPermissions('ReconciliationStatementView') && props.row.reconciled_rows < props.row.total_rows" color="green" class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn"
            style="font-size: 12px" label="Reconcile" :to="`/bank-reconciliation/reconcile/?account_id=${props.row.account.id}&start_date=${props.row.start_date}&end_date=${props.row.end_date}`" />
          <q-btn v-else-if="checkPermissions('ReconciliationStatementView')" color="blue" class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn" style="font-size: 12px" label="Reconciled"
            disable />
          <q-btn v-if="checkPermissions('ReconciliationStatementDelete')" color="red" class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn" style="font-size: 12px" label="Delete"
            @click="deleteStatement(props.row.id)" />
        </q-td>
      </template>
      <template v-slot:body-cell-category="props">
        <q-td :props="props">
          <router-link v-if="checkPermissions('CategoryModify')" style="font-weight: 500; text-decoration: none" class="text-blue" :to="`/account-category/${props.row.category.id}/`">{{
            props.row.category.name
            }}</router-link>
          <span v-else>{{ props.row.category.name }}</span>
        </q-td>
      </template>
      <template v-slot:body-cell-account="props">
        <q-td :props="props">
          <router-link v-if="checkPermissions('AccountView')" :to="`/account/${props.row.account.id}/view/?start_date=${props.row.start_date}&end_date=${props.row.end_date}`"
            style="font-weight: 500; text-decoration: none" class="text-blue">
            {{ props.row.account.name }}
          </router-link>
          <span v-else>{{ props.row.account.name }}</span>
        </q-td>
      </template>
      <template v-slot:body-cell-rows_update="props">
        <q-td :props="props">
          <div v-if="props.row.has_updated_rows" class="flex gap-4 items-center bg-yellow-500 p-2 rounded-md w-fit">
            <div>
              <!-- Show message -->
              Some rows have been updated and might need your attention
            </div>
            <q-btn color="yellow" class="text-black q-py-none q-px-md font-size-sm q-mr-md l-view-btn" style="font-size: 12px" label="View Updated Rows"
              @click="fetchUpdatedTransactions(props.row.id)" />
          </div>
        </q-td>
      </template>
      <!-- no-data -->
      <template v-slot:no-data>
        <div class="text-h7 text-center">No data available</div>
      </template>
    </q-table>
  </div>


  <q-dialog no-shake v-model="statementPrompt">
    <q-card style="min-width: 350px" class="p-5 space-y-3">
      <div class="text-xl text-gray-700 font-bold">
        Statement Upload
      </div>
      <q-form @submit="submitStatement">

        <n-auto-complete v-model="statementAccount" optionValue="ledger_id" :options="bankAccounts" label="Bank Accounts" />
        <!-- date formats -->
        <q-select v-model="selectedDateFormat" :options="dateFormats" label="Date Format as in the statement" :error="false" />
        <q-file v-if="selectedDateFormat" bottom-slots v-model="statementSheet" label="Statement Document" counter max-files="1" accept=".xlsx, .xls" class="q-mb-md"
          @update:model-value="parseExcelFile">
          <template v-slot:prepend>
            <q-icon name="cloud_upload" @click.stop.prevent />
          </template>
          <template v-slot:append>
            <q-icon v-if="statementSheet" name="close" @click.stop.prevent="removeStatement" class="cursor-pointer" />
          </template>

          <template v-slot:hint>
            <div v-if="!statementSheet" class="text-gray-600">Upload your statement document here</div>
            <div v-else-if="isStatementProcessing" class="text-gray-600">Processing...</div>
            <div v-else-if="hasError" class="text-red-600 text-xs">Error parsing the file</div>
            <div v-else-if="toHaveHeaders.find(header => !statementHeaders.has(header))" class="text-red-600 text-xs">Couldn't find header columns: {{
              toHaveHeaders.filter(header => !statementHeaders.has(header)).join(', ') }}</div>
            <div v-else-if="statementData.length" class="text-green-600 text-xs">
              {{ statementData.length }} rows parsed</div>
          </template>
        </q-file>

        <div>
          <DateRangePicker v-model:startDate="statementStartDate" v-model:endDate="statementEndDate" :hide-btns="true" id="modal-date-picker" />
          <div class="text-gray-600 -mt-4 text-xs">
            Please select the date range for the statement you want to extract <br> <span class=" ">If not selected, the system will use the date range from the statement</span>
          </div>
        </div>
        <div>
          <q-checkbox class="-ml-2.5 mt-3 text-gray-600" v-model="mergeDescription" label="Merge transactions with similar description" />
        </div>

        <div class="text-right !mt-6">
          <q-btn type="submit" :loading="isLoading" label="Upload" color="green"
            :disable="!statementAccount || !statementSheet || isStatementProcessing || toHaveHeaders.find(header => !statementHeaders.has(header))" />
        </div>
      </q-form>
    </q-card>
  </q-dialog>

  <q-dialog v-model="openUpdateDialog">
    <q-card style="min-width: 900px">
      <div class="bg-white shadow-lg rounded-lg overflow-hidden border">
        <div v-if="updatedData?.results.length" class="p-4 bg-gray-50 max-h-[800px] overflow-y-auto matched-transactions">
          <q-infinite-scroll ref="infiniteScroll" @load="loadMore" :offset="250" scroll-target=".matched-transactions">
            <div v-for="data in updatedData?.results" :key="data.statement_transactions[0].id" class="border-b-2 mb-5 pb-5">
              <div class="grid grid-cols-2 gap-4">
                <div class="flex flex-col">
                  <div class="bg-white border rounded-lg shadow-sm overflow-hidden grow">
                    <div class="px-4 py-2 border-b bg-blue-50 text-blue-700 font-semibold">
                      Statement
                    </div>
                    <div class="divide-y text-xs">
                      <div v-for="transaction in data.statement_transactions" :key="transaction.id" class="px-4 py-2.5">
                        <div class="flex justify-between mb-1">
                          <span class="text-gray-500">{{ transaction.date }}</span>
                          <div class="font-medium">
                            <span v-if="transaction.dr_amount" class="text-red-500">-{{ transaction.dr_amount }}</span>
                            <span v-if="transaction.cr_amount" class="text-green-500">+{{ transaction.cr_amount }}</span>
                          </div>
                        </div>
                        <div class="text-gray-600">{{ transaction.description }}</div>
                      </div>
                    </div>

                  </div>
                  <div class="px-4 py-2 text-right">
                    <span :class="Number(calculateTotal(data.statement_transactions, true)) < 0 ? 'text-red-500' : 'text-green-500'">{{ calculateTotal(data.statement_transactions, true) }}</span>
                  </div>
                </div>

                <!-- System Transactions -->
                <div class="flex flex-col">
                  <div class="bg-white border rounded-lg shadow-sm overflow-hidden grow">
                    <div class="px-4 py-2 border-b bg-green-50 text-green-700 font-semibold">
                      System
                      <!-- Add links -->
                      <span v-for="source, index in filterSources(data.system_transactions)" :key="source.source_id">
                        <router-link target="_blank" :to="source.url" class="text-blue-800 decoration-none text-xs">
                          {{ source.source_type }}
                        </router-link>
                        <span v-if="index < filterSources(data.system_transactions).length - 1">, </span>
                      </span>

                    </div>
                    <div class="divide-y text-sm">
                      <div v-for="transaction, index in data.system_transactions" :key="transaction.id"
                        class="px-4 py-3  border-gray-200 hover:bg-gray-50 transition-colors duration-200 relative group" :class="{ 'border-b': index !== data.system_transactions.length - 1 }">

                        <div class="text-xs">
                          <div class="text-gray-500">{{ transaction.date }}</div>

                          <div v-for="counterpart in transaction.counterpart_accounts" :key="counterpart.account_id" class="flex justify-between">
                            <div class="text-gray-700 truncate flex-grow mr-2">
                              {{ counterpart.account_name }}
                            </div>
                            <div class="flex space-x-2">
                              <span v-if="counterpart.dr_amount" class="text-red-600 font-medium">
                                -{{ counterpart.dr_amount }}
                              </span>
                              <span v-if="counterpart.cr_amount" class="text-green-600 font-medium">
                                +{{ counterpart.cr_amount }}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="px-4 py-2 text-right">
                    <span :class="Number(calculateTotalFromCounterparts(data.system_transactions)) < 0 ? 'text-red-500' : 'text-green-500'">{{
                      calculateTotalFromCounterparts(data.system_transactions)
                      }}</span>
                  </div>
                </div>
              </div>
              <div class="flex justify-end space-x-3">
                <button @click="
                  updateTransactions(data)
                  " class="px-3 py-1.5 bg-green-500 text-white text-sm rounded-md hover:bg-green-600 transition-colors">
                  Reconcile
                </button>
                <button @click="unmatchMatchedTransactions(data)" class="px-3 py-1.5 bg-red-500 text-white text-sm rounded-md hover:bg-red-600 transition-colors">
                  Unmatch
                </button>
              </div>
            </div>
            <template v-slot:loading>
              <div class="row justify-center q-my-md">
                <q-spinner-dots color="primary" size="40px" />
              </div>
            </template>
          </q-infinite-scroll>
        </div>
      </div>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import * as XLSX from 'xlsx'
import { Ref } from 'vue'
import checkPermissions from 'src/composables/checkPermissions'
import { getVoucherUrl, getPermissionFromSourceType } from 'src/composables/getVoucherUrlAndPermissions'


interface SystemTransactionData {
  id: number
  date: string
  dr_amount: string | null
  cr_amount: string | null
  source_type: string
  source_id: number
  counterpart_accounts: {
    account_id: number
    account_name: string
    dr_amount: string
    cr_amount: string
  }[]
}

interface StatementTransactionData {
  id: number
  date: string
  dr_amount: string | null
  cr_amount: string | null
  balance: string
  description: string
  transaction_ids: number[]
}

const $q = useQuasar()
const openUpdateDialog = ref(false)
type Response = {
  pagination: {
    pages: number
  },
  results: {
    statement_transactions: StatementTransactionData[]
    system_transactions: SystemTransactionData[]
  }[]
}

const updatedData: Ref<Response> = ref({
  pagination: {
    pages: 0
  },
  results: []
})
const infiniteScroll = ref()

const statementAccount = ref(null)
const bankAccounts = ref([])
const statementStartDate = ref()
const statementEndDate = ref()

const statementPrompt = ref(false)
const statementSheet = ref(null)
const statementHeaders = ref(new Set())

const statementData: Ref<Record<string, any>[]> = ref([])
const isStatementProcessing = ref(false)
const hasError = ref(false)
const mergeDescription = ref(false)

const endpoint = 'v1/bank-reconciliation/defaults/'
const isLoading = ref(false)

useApi(endpoint).then((response) => {
  bankAccounts.value = response.banks
})
const page = ref(1)
const rowId = ref()

const fetchUpdatedTransactions = async (id: number) => {
  rowId.value = id
  await useApi(`v1/bank-reconciliation/${id}/updated-transactions/?page=${page.value}`).then((response) => {
    updatedData.value = response
    openUpdateDialog.value = true
  })
}


const deleteStatement = (id: number) => {
  $q.dialog({
    title: '<span class="text-red">Delete?</span>',
    message: 'All the transactions will be unreconciled and the statement will be deleted.',
    cancel: true,
    html: true,
  }).onOk(() => {
    useApi(`v1/bank-reconciliation/${id}/`, {
      method: 'DELETE'
    }).then(() => {
      $q.notify({
        color: 'green-6',
        message: 'Statement deleted successfully',
        icon: 'check_circle',
        position: 'top-right',
      })
      onFilterUpdate()
    }).catch((error) => {
      console.log(error)
      $q.notify({
        color: 'red-6',
        message: 'Failed to delete statement',
        icon: 'error',
        position: 'top-right',
      })
    })
  })
}


const loadMore = async (index: number, done: any) => {
  // see if there are more pages
  if (page.value < updatedData.value.pagination.pages) {
    page.value += 1
    await fetchUpdatedTransactions(rowId.value)
  } else {
    infiniteScroll.value.stop()
  }
  done()
}


const calculateTotal = (transactions: SystemTransactionData[] | StatementTransactionData[], forStatement = false) => {
  let cr_amount = 0
  let dr_amount = 0
  for (let transaction of transactions) {
    if (transaction.cr_amount) {
      cr_amount += Number(transaction.cr_amount)
    }
    if (transaction.dr_amount) {
      dr_amount += Number(transaction.dr_amount)
    }
  }
  if (forStatement) {
    return (cr_amount - dr_amount).toFixed(2)
  }
  return (dr_amount - cr_amount).toFixed(2)
}

const calculateTotalFromCounterparts = (counterparts: { dr_amount: string | null, cr_amount: string | null }[]) => {
  let cr_amount = 0
  let dr_amount = 0
  for (let counterpart of counterparts) {
    if (counterpart.cr_amount) {
      cr_amount += Number(counterpart.cr_amount)
    }
    if (counterpart.dr_amount) {
      dr_amount += Number(counterpart.dr_amount)
    }
  }
  return (dr_amount - cr_amount).toFixed(2)
}


const filterSources = (systemTransactions: SystemTransactionData[]): { source_id: number, url: string, source_type: string }[] => {
  const sourceMap = new Map<number, { source_id: number, url: string, source_type: string }>()

  systemTransactions.forEach((transaction: SystemTransactionData) => {
    if (transaction.source_id) {
      // check permission
      if (checkPermissions(getPermissionFromSourceType(transaction.source_type))) {
        const url = getVoucherUrl(transaction)
        if (url) {
          // Use source_id as the unique key
          if (!sourceMap.has(transaction.source_id)) {
            sourceMap.set(transaction.source_id, {
              source_id: transaction.source_id,
              source_type: transaction.source_type,
              url,
            })
          }
        }
      }
    }
  })

  return Array.from(sourceMap.values())
}




const unmatchMatchedTransactions = (matchedTransaction: {
  statement_transactions: StatementTransactionData[]
  system_transactions: SystemTransactionData[]
}) => {
  console.log('Unmatching:', matchedTransaction)
  useApi('v1/bank-reconciliation/unmatch-transactions/', {
    method: 'POST',
    body: {
      statement_ids: matchedTransaction.statement_transactions.map(t => t.id),
    }
  }).then(() => {
    const index = updatedData.value?.results.findIndex(group => group === matchedTransaction)
    if (index > -1) {
      updatedData.value?.results.splice(index, 1)
    }
    $q.notify({
      color: 'green-6',
      message: 'Transactions unmatched successfully',
      icon: 'check_circle',
      position: 'top-right',
    })
    if (updatedData.value?.results.length === 0) {
      openUpdateDialog.value = false
    }

  }).catch((error) => {
    console.log(error)
    $q.notify({
      color: 'red-6',
      message: 'Failed to unmatch transactions',
      icon: 'error',
      position: 'top-right',
    })
  })
}

const updateTransactions = (matchedTransaction: {
  statement_transactions: StatementTransactionData[]
  system_transactions: SystemTransactionData[]
}) => {
  console.log('Reconciling:', matchedTransaction)
  useApi('v1/bank-reconciliation/update-transactions/', {
    method: 'POST',
    body: {
      statement_ids: matchedTransaction.statement_transactions.map(t => t.id),
      transaction_ids: matchedTransaction.system_transactions.map(t => t.id),
    }
  }).then(() => {
    const index = updatedData.value?.results.findIndex(group => group === matchedTransaction)
    if (index > -1) {
      updatedData.value?.results.splice(index, 1)
    }
    $q.notify({
      color: 'green-6',
      message: 'Transactions reconciled successfully',
      icon: 'check_circle',
      position: 'top-right',
    })
    if (updatedData.value?.results.length === 0) {
      openUpdateDialog.value = false
    }
    onFilterUpdate()
  }).catch((error) => {
    console.log(error)
    $q.notify({
      color: 'red-6',
      message: 'Failed to reconcile transactions',
      icon: 'error',
      position: 'top-right',
    })
  })
}



const listEndpoint = '/v1/bank-reconciliation/'
const {
  rows,
  resetFilters,
  filters,
  loading,
  searchQuery,
  pagination,
  onRequest,
  onFilterUpdate,
} = useList(listEndpoint)

type MappingFunction = (header: string) => string

const toHaveHeaders = ['date', 'dr_amount', 'cr_amount', 'balance']

const headerMappings: { [key: string]: string | MappingFunction } = {
  id: 'id',
  'txn date': 'date',
  'chequeno': 'cheque_no',
  'chequeno.': 'cheque_no',
  'debit(npr)': 'dr_amount',
  'credit(npr)': 'cr_amount',
  'balance(npr)': 'balance',
  'txn no.': 'txn_no',
  'txn no': 'txn_no',
  'transaction date': 'date',
  'withdraw': 'dr_amount',
  'deposit': 'cr_amount',
}

function mapHeaders(headers: string[]): string[] {
  return headers.map((header) => {
    const lowerHeader = header
      .toLowerCase()
      .replace(/[\n\t]/g, ' ')
      .replace(/\s{2,}/g, ' ')
    const mapping = headerMappings[lowerHeader]
    if (typeof mapping === 'function') {
      return mapping(header)
    }
    return mapping || header
  })
}

const removeStatement = () => {
  statementSheet.value = null
  statementData.value = []
  statementHeaders.value = new Set()
}


const submitStatement = async () => {
  if (!statementAccount.value || !statementData.value.length) {
    return
  }
  isLoading.value = true

  useApi('v1/bank-reconciliation/import-statement/', {
    method: 'POST',
    body: {
      account_id: statementAccount.value,
      transactions: statementData.value,
      start_date: statementStartDate.value,
      end_date: statementEndDate.value,
      merge_description: mergeDescription.value
    }
  }).then(() => {
    $q.notify({
      color: 'green-6',
      message: 'Statement uploaded, please wait while we process the data',
      icon: 'check_circle',
      position: 'top-right',
    })
    statementPrompt.value = false
  }).catch((error) => {
    $q.notify({
      color: 'red-6',
      message: error.data?.detail || 'Something went wrong',
      icon: 'report_problem',
      position: 'top-right',
    })
  }).finally(() => {
    isLoading.value = false
  })
}

const selectedDateFormat = ref()

const dateFormats = [
  'YYYY MM DD',
  'DD MM YYYY',
  'MM DD YYYY',
  'YY MM DD',
  'DD MM YY',
  'MM DD YY',
]

function parseDate(dateString: string | null): string {
  if (!dateString) {
    throw new Error('Date string is empty')
  }
  console.log(dateString)
  // if date contains any special characters, replace them with -
  dateString = dateString.replace(/[^0-9]/g, '-')

  let date = dateString
  if (selectedDateFormat.value === 'YY MM DD') {
    const [year, month, day] = dateString.split('-')
    date = `20${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
  }
  if (selectedDateFormat.value === 'DD MM YY') {
    const [day, month, year] = dateString.split('-')
    date = `20${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
  }
  if (selectedDateFormat.value === 'MM DD YY') {
    const [month, day, year] = dateString.split('-')
    date = `20${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
  }
  return new Date(date).toISOString().split('T')[0]

}

const columns = [{ 'name': 'account', 'label': 'Account', 'align': 'left', 'field': 'account' },
{ 'name': 'start_date', 'label': 'Start date', 'align': 'left', 'field': 'start_date' },
{ 'name': 'end_date', 'label': 'End date', 'align': 'left', 'field': 'end_date' },
{ 'name': 'total_rows', 'label': 'Total rows', 'align': 'left', 'field': 'total_rows' },
{ 'name': 'reconciled_rows', 'label': 'Reconciled rows', 'align': 'left', 'field': 'reconciled_rows' },
{
  'name': 'rows_update', 'label': '', 'align': 'left', 'field': 'rows_update'

}, { 'name': 'actions' }]



function parseXLSXSheet(sheetData: any[][]): any[] {
  let headerRowIndex = sheetData.findIndex(row =>
    row.some(cell => {
      const lowerCasedCell = String(cell).toLowerCase().trim()
      return lowerCasedCell.includes('debit') || lowerCasedCell.includes('credit') || lowerCasedCell.includes('description')
    })
  )
  // If no header row found, throw an error
  if (headerRowIndex === -1) {
    console.warn('No header row found in the sheet')
    return []
  }
  let headerRow = sheetData[headerRowIndex].map((e: string) =>
    e?.trim()
      .toLowerCase()
      .replace(/[\n\t]/g, ' ')
      .replace(/\d/g, '') || ''
  )

  headerRow = mapHeaders(headerRow)

  statementHeaders.value = new Set([...statementHeaders.value, ...headerRow])

  interface ParsedData {
    [id: string]: any
  }

  const data: ParsedData[] = []
  for (let rowIndex = headerRowIndex + 1; rowIndex < sheetData.length; rowIndex++) {
    const row = sheetData[rowIndex]
    const rowData: ParsedData = {}

    const hasBalance = row.some((cell, index) =>
      ['balance'].includes(headerRow[index]) && cell
    )
    if (!hasBalance) {
      continue
    }

    for (let index = 0; index < row.length; index++) {
      const cell = row[index]
      const header = headerRow[index]

      if (!header) {
        continue
      }
      rowData[header] = cell

      if (header === 'date') {
        rowData.date = /^\d{4}-\d{2}-\d{2}$/.test(cell) ? cell : parseDate(cell)
      }

    }
    if (rowData.description.toLowerCase().includes('closing balance')) {
      return data
    }
    if (rowData.description.toLowerCase().includes('opening balance')) {
      continue
    }
    data.push(rowData)
  }
  return data
}

function fileToArrayBuffer(file: File): Promise<ArrayBuffer> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsArrayBuffer(file)

    reader.onload = () => {
      if (reader.result instanceof ArrayBuffer) {
        resolve(reader.result)
      } else {
        reject(new Error('File could not be read as an ArrayBuffer'))
      }
    }

    reader.onerror = () => {
      reject(new Error('Failed to read file as ArrayBuffer'))
    }
  })
}


async function parseExcelFile(file: File): Promise<void> {
  isStatementProcessing.value = true
  statementData.value = []
  hasError.value = false
  try {

    await fileToArrayBuffer(file).then((arrayBuffer) => {
      const workbook = XLSX.read(arrayBuffer, { type: 'array' })
      workbook.SheetNames.forEach((sheetName) => {
        const worksheet = workbook.Sheets[sheetName]
        // const sheetData = XLSX.utils.sheet_to_json(worksheet, { header: 1,  raw: true }) as any[][]
        // Apply formatting
        const formattedData = []
        const range = XLSX.utils.decode_range(worksheet['!ref'] ?? '') // Get the sheet range

        for (let rowNum = range.s.r; rowNum <= range.e.r; rowNum++) {
          const row = []
          for (let colNum = range.s.c; colNum <= range.e.c; colNum++) {
            const cellAddress = XLSX.utils.encode_cell({ r: rowNum, c: colNum })
            const cell = worksheet[cellAddress]
            if (cell) {
              // Format the cell if it exists
              row.push(XLSX.utils.format_cell(cell))
            } else {
              // Push an empty value if the cell is undefined
              row.push(null)
            }
          }
          formattedData.push(row)
        }
        const parsedData = parseXLSXSheet(formattedData)
        const filteredData = parsedData.filter((row) => Object.keys(row).length > 0)
        statementData.value.push(...filteredData)
      })
    })
  }
  catch (e) {
    console.log(e)
    hasError.value = true
  }
  isStatementProcessing.value = false
}

</script>
