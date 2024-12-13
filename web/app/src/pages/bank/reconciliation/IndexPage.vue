<template>
  <q-page class="p-10">
    <div class="flex justify-between">
      <div class="flex gap-5">
        <n-auto-complete v-model="selectedAccount" :options="bankAccounts" endpoint="v1/bank-reconciliation/create-defaults" label="Bank Accounts" optionValue="ledger_id" />
        <DateRangePicker v-model:startDate="startDate" v-model:endDate="endDate" :hide-btns="true" />
        <div>
          <q-btn icon="mdi-magnify" color="primary" label="Search" @click="fetchTransactions" :disable="!selectedAccount || !startDate || !endDate ? true : false" />
        </div>
      </div>
      <div>
        <q-btn icon="mdi-file-upload-outline" color="green" label="Upload Statement" @click="statementPrompt = true"></q-btn>
      </div>
    </div>
    <q-dialog no-shake v-model="statementPrompt">
      <q-card style="min-width: 350px" class="p-5 space-y-3">
        <div class="text-xl text-gray-700 font-bold">
          Statement Upload
        </div>
        <q-form @submit="submitStatement">

          <n-auto-complete v-model="statementAccount" optionValue="ledger_id" :options="bankAccounts" endpoint="v1/bank-reconciliation/create-defaults" label="Bank Accounts" />
          <!-- date formats -->
          <q-select v-model="selectedDateFormat" :options="dateFormats" label="Date Format as in the statement" :error="false" />
          <q-file v-if="selectedDateFormat" bottom-slots v-model="statementSheet" label="Statement Document" counter max-files="1" accept=".csv, .xlsx, .xls" class="q-mb-md"
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
            </template>
          </q-file>

          <div>
            <DateRangePicker v-model:startDate="statementStartDate" v-model:endDate="statementEndDate" :hide-btns="true" id="modal-date-picker" />
            <div class="text-gray-600 -mt-4 text-xs">
              Please select the date range for the statement you are uploading (optional)
            </div>
          </div>

          <div class="text-right !mt-6">
            <q-btn type="submit" label="Upload" color="green" :disable="!statementAccount || !statementSheet || isStatementProcessing || toHaveHeaders.find(header => !statementHeaders.has(header))" />
          </div>
        </q-form>
      </q-card>
    </q-dialog>
    <!-- Table -->
    <BankReconciliationTable v-if="systemTransactionData.length && statementTransactionData.length" :systemTransactionData="systemTransactionData"
      :statementTransactionData="statementTransactionData" />
  </q-page>
</template>

<script setup lang="ts">
import * as XLSX from 'xlsx'
import { Ref } from 'vue'

const selectedAccount = ref(null)
const statementAccount = ref(null)
const bankAccounts = ref([])
const startDate = ref('2024-11-08')
const endDate = ref('2024-12-08')
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

const endpoint = 'v1/bank-reconciliation/banks/'

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
  })
}


const fetchTransactions = async () => {
  if (!selectedAccount.value || !startDate.value || !endDate.value) {
    return
  }

  useApi('v1/bank-reconciliation/unreconciled-transactions/?start_date=' + startDate.value + '&end_date=' + endDate.value + '&account_id=' + selectedAccount.value).then((response) => {
    systemTransactionData.value = response.system_transactions
    statementTransactionData.value = response.statement_transactions
  }).catch((error) => {
    console.log(error)
    systemTransactionData.value = []
    statementTransactionData.value = []
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
      const lowerCasedCell = String(cell).toLowerCase()
      return lowerCasedCell.includes('debit') || lowerCasedCell.includes('credit')
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
  ).filter(Boolean)

  headerRow = mapHeaders(headerRow)

  statementHeaders.value = new Set([...statementHeaders.value, ...headerRow])

  interface ParsedData {
    [id: string]: any
  }

  const data: ParsedData[] = []

  sheetData.slice(headerRowIndex + 1).forEach(row => {
    const rowData: ParsedData = {}
    row.forEach((cell, index) => {
      rowData[headerRow[index]] = cell

      if (headerRow[index] === 'date') {
        if (/^\d{4}-\d{2}-\d{2}$/.test(cell)) {
          rowData['date'] = cell
        } else {
          rowData['date'] = parseDate(cell)
        }
      }

    })
    data.push(rowData)
  })

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
