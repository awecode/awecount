<template>
  <q-page class="p-10">
    <div class="flex justify-between">
      <div class="flex gap-5">
        <n-auto-complete v-model="selectedAccount" :options="bankAccounts" label="Bank Accounts" optionValue="ledger_id" />
        <DateRangePicker v-model:startDate="startDate" v-model:endDate="endDate" :hide-btns="true" />
        <div>
          <q-btn :loading="isLoading" icon="mdi-magnify" color="primary" label="Search" @click="fetchTransactions" :disable="!selectedAccount || !startDate || !endDate ? true : false" />
        </div>
      </div>
      <div>
        <!-- <q-btn icon="mdi-file-upload-outline" color="green" label="Go to List" @click="router.push('/bank/reconciliation')" /> -->
      </div>
    </div>
    <BankReconciliationTable v-if="systemTransactionData.length && statementTransactionData.length" :systemTransactionData="systemTransactionData" :statementTransactionData="statementTransactionData"
      :acceptableDifference="acceptableDifference" />
  </q-page>
</template>

<script setup lang="ts">
import * as XLSX from 'xlsx'
import { Ref } from 'vue'
const $q = useQuasar()
const route = useRoute()
const router = useRouter()

const selectedAccount = ref(route.query.account_id || null)
const statementAccount = ref(null)
const bankAccounts = ref([])
const startDate = ref(route.query.start_date as string || '2024-11-08')
const endDate = ref(route.query.end_date as string || '2024-12-08')
const statementStartDate = ref()
const statementEndDate = ref()

const statementPrompt = ref(false)
const statementSheet = ref(null)
const statementHeaders = ref(new Set())

const statementData: Ref<Record<string, any>[]> = ref([])
const isStatementProcessing = ref(false)
const hasError = ref(false)
const systemTransactionData = ref([])
const statementTransactionData = ref([])
const acceptableDifference = ref(0.01)

const endpoint = 'v1/bank-reconciliation/banks/'
const isLoading = ref(false)

useApi(endpoint).then((response) => {
  bankAccounts.value = response
})

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
  }).then((response) => {
    console.log(response)
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


const fetchTransactions = async () => {
  if (!selectedAccount.value || !startDate.value || !endDate.value) {
    return
  }
  isLoading.value = true
  router.push({
    query: {
      account_id: selectedAccount.value,
      start_date: startDate.value,
      end_date: endDate.value,
    }
  })

  useApi('v1/bank-reconciliation/unreconciled-transactions/?start_date=' + startDate.value + '&end_date=' + endDate.value + '&account_id=' + selectedAccount.value).then((response) => {
    systemTransactionData.value = response.system_transactions
    statementTransactionData.value = response.statement_transactions
    acceptableDifference.value = response.acceptable_difference
  }).catch((error) => {
    console.log(error)
    systemTransactionData.value = []
    statementTransactionData.value = []
  }).finally(() => {
    isLoading.value = false
  })
}

if (selectedAccount.value && startDate.value && endDate.value) {
  fetchTransactions()
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
      if (header === 'description') {
        console.log(cell)
        if (cell.trim() === 'Opening Balance') {
          continue
        }
        if (cell.trim() === 'Closing Balance') {
          return data
        }
      }

      rowData[header] = cell

      if (header === 'date') {
        rowData.date = /^\d{4}-\d{2}-\d{2}$/.test(cell) ? cell : parseDate(cell)
      }

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
