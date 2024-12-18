<template>
  <div class="q-pa-md">
    <div class="row justify-end">
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
          <q-btn v-if="checkPermissions('ReconciliationStatementView') && props.row.reconciled_entries < props.row.total_entries" color="blue" class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn"
            style="font-size: 12px" label="Reconcile" :to="`/bank-reconciliation/reconcile/?account_id=${props.row.account.id}&start_date=${props.row.start_date}&end_date=${props.row.end_date}`" />
          <q-btn v-else-if="checkPermissions('ReconciliationStatementView')" color="blue" class="q-py-none q-px-md font-size-sm q-mr-md l-view-btn" style="font-size: 12px" label="Reconciled"
            disable />
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

        <div class="text-right !mt-6">
          <q-btn type="submit" :loading="isLoading" label="Upload" color="green"
            :disable="!statementAccount || !statementSheet || isStatementProcessing || toHaveHeaders.find(header => !statementHeaders.has(header))" />
        </div>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import * as XLSX from 'xlsx'
import { Ref } from 'vue'
import checkPermissions from 'src/composables/checkPermissions'

const $q = useQuasar()

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

const endpoint = 'v1/bank-reconciliation/banks/'
const isLoading = ref(false)

useApi(endpoint).then((response) => {
  bankAccounts.value = response
})

const listEndpoint = '/v1/bank-reconciliation/'
const {
  rows,
  columns,
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
    e.trim()
      .toLowerCase()
      .replace(/[\n\t]/g, ' ')
      .replace(/\d/g, '')
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
        const sheetData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][]
        const parsedData = parseXLSXSheet(sheetData)
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
