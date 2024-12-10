<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn color="blue" label="Export" icon-right="download" @click="onDownloadXls" class="export-btn" />
      <q-btn color="blue" label="Import" icon-right="upload" @click="openImportModal" class="import-btn" />
      <q-btn v-if="checkPermissions('SalesCreate')" color="green" to="/sales-voucher/add/" label="New Sales"
        icon-right="add" class="add-btn" />
    </div>
    <q-table :rows="rows" :columns="newColumn" :loading="loading" :filter="searchQuery" v-model:pagination="pagination"
      row-key="id" @request="onRequest" class="q-mt-md" :rows-per-page-options="[20]">
      <template v-slot:top>
        <div class="search-bar">
          <q-input dense debounce="500" v-model="searchQuery" placeholder="Search" class="full-width search-input">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
          <q-btn class="f-open-btn" icon="mdi-filter-variant">
            <q-menu>
              <div class="menu-wrapper" style="width: min(550px, 90vw)">
                <div style="border-bottom: 1px solid lightgrey">
                  <h6 class="q-ma-md text-grey-9">Filters</h6>
                </div>
                <div class="q-ma-sm">
                  <div class="q-mb-sm">
                    <q-checkbox v-model="filters.is_due" label="Is Due?" :false-value="null"></q-checkbox>
                  </div>
                  <div class="q-ma-sm">
                    <MultiSelectChip :options="[
                      'Draft',
                      'Issued',
                      'Paid',
                      'Partially Paid',
                      'Cancelled',
                    ]" v-model="filters.status" />
                  </div>
                </div>
                <div class="q-mx-md">
                  <DateRangePicker v-model:startDate="filters.start_date" v-model:endDate="filters.end_date" />
                </div>
                <div class="q-mx-sm">
                  <n-auto-complete-v2 v-model="filters.payment_mode" endpoint="v1/payment-modes/choices/"
                    label="Payment Mode" :fetchOnMount="true" />
                </div>
                <div class="q-mx-md row q-mb-md q-mt-lg">
                  <q-btn color="green" label="Filter" class="q-mr-md f-submit-btn" @click="onFilterUpdate"></q-btn>
                  <q-btn color="red" icon="close" @click="resetFilters" class="f-reset-btn"></q-btn>
                </div>
              </div>
            </q-menu>
          </q-btn>
        </div>
      </template>
      <template v-slot:body-cell-date="props">
        <q-td data-testid="SN">
          {{ props.row.date }}
        </q-td>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <div class="row align-center justify-center" data-testid="status">
            <div class="text-white text-subtitle row items-center justify-center" :class="props.row.status == 'Issued'
              ? 'bg-blue-2 text-blue-10'
              : props.row.status == 'Paid'
                ? 'bg-green-2 text-green-10'
                : props.row.status == 'Draft'
                  ? 'bg-orange-2 text-orange-10'
                  : props.row.status == 'Partially Paid' ? 'bg-green-1 text-green-6'
                    : 'bg-red-2 text-red-10'
              " style="border-radius: 8px; padding: 2px 10px">
              {{ props.row.status }}
            </div>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-party_name="props">
        <q-td :props="props">
          <div v-if="props.row.customer_name" class="row align-center text-subtitle2 text-grey-8">
            <!-- We neeed to know show party icons if both customer name and party name is available, as that means customer name is actually an alias of that party -->
            <q-icon v-if="props.row.party_name" name="domain" size="sm" class="text-grey-8 q-mr-sm"></q-icon>
            {{ props.row.customer_name }}
          </div>
          <div v-else>
            <q-icon name="domain" size="sm" class="text-grey-8"></q-icon>
            <span class="text-capitalize q-ml-sm text-subtitle2 text-grey-8">
              {{ props.row.party_name }}
            </span>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <div class="row q-gutter-x-md justify-start">
            <q-btn v-if="checkPermissions('SalesView')" color="blue" label="View"
              class="q-py-none q-px-md font-size-sm l-view-btn" style="font-size: 12px"
              :to="`/sales-voucher/${props.row.id}/view/`" data-testid="view-btn" />
          </div>
        </q-td>

        <!-- TODO: add modals -->
      </template>
      <template v-slot:body-cell-payment_receipts="props">
        <q-td :props="props">
          <span v-for="id in props.row.payment_receipts.map((item) => item.id)" :key="id">
            <router-link v-if="checkPermissions('PaymentReceiptView')" :to="`/payment-receipt/${id}/view/`"
              style="font-weight: 500; text-decoration: none" class="text-blue">
              #{{ id }}
            </router-link>
            <span v-else>#{{ id }}</span>
          </span>
        </q-td>
      </template>
      <template v-slot:body-cell-voucher_no="props">
        <q-td :props="props">
          <span v-if="checkPermissions('SalesView')" data-testid="voucher-no">
            <router-link v-if="checkPermissions('SalesView') && props.row.voucher_no"
              :to="`/sales-voucher/${props.row.id}/view/`" style="font-weight: 500; text-decoration: none"
              class="text-blue">
              {{ props.row.voucher_no }}
            </router-link>
          </span>
          <span v-else data-testid="voucher-no">
            {{ props.row.voucher_no }}
          </span>
        </q-td>
      </template>
      <template v-slot:body-cell-receipt_amount="props">
        <td>
          <!-- {{ props.row.payment_receipts.map((item) => item.amount) }} -->
          {{ $nf(props.row.payment_receipts.reduce((a, b) => (a.amount || 0) + (b.amount || 0), 0))
          }}
        </td>
      </template>
      <template v-slot:body-cell-tds="props">
        <td>
          <!-- {{ props.row.payment_receipts.map((item) => item.amount) }} -->
          {{ $nf(props.row.payment_receipts.reduce((a, b) => (a.tds_amount || 0) + (b.tds_amount || 0), 0)) }}
        </td>
      </template>
    </q-table>
    <q-dialog v-model="showImportModal">
      <q-card style="min-width: min(40vw, 500px)" class="overflow-visible">
        <q-card-section class="bg-primary flex justify-between">
          <div class="text-h6 text-white">
            <span>Import Sales Invoices</span>
          </div>
          <q-btn icon="close" class="text-primary bg-slate-200 opacity-95" flat round dense @click="closeImportModal" />
        </q-card-section>

        <q-card-section class="q-ma-md">
          <p class="text-caption">Upload a .xlsx file to import sales invoices
            <a href="/files/sales-invoices.xlsx" download="sample-sales-invoices.xlsx" class="text-primary">Download sample
              file</a>
          </p>
          <q-file @input="validateImportFile" v-model="fileToImport" accept=".xlsx" label="Select file" color="primary"
            flat dense :disable="isImporting">
          </q-file>
          <p v-if="importFileParseError" class="text-red-600">
            {{ importFileParseError }}
          </p>
          <div class="text-right q-mt-lg">
            <q-btn label="Import" color="primary" @click="importInvoices(fileToImport)"
              :disable="isImporting || !fileToImport || importFileParseError"></q-btn>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
import * as XLSX from 'xlsx'

export default {
  setup() {
    const metaData = {
      title: 'Sales Invoices | Awecount',
    }
    useMeta(metaData)
    const endpoint = '/v1/sales-voucher/'
    const listData = useList(endpoint)
    const route = useRoute()
    const onDownloadXls = () => {
      const query = route.fullPath.slice(route.fullPath.indexOf('?'))
      useApi('v1/sales-voucher/export' + query)
        .then((data) =>
          usedownloadFile(
            data,
            'application/vnd.ms-excel',
            'Sales_voucher'
          )
        )
        .catch((err) => console.log('Error Due To', err))
    }
    const newColumn = [
      {
        name: 'voucher_no',
        label: 'Voucher no',
        align: 'left',
        field: 'voucher_no',
        sortable: true
      },
      {
        name: 'party_name',
        label: 'Party name',
        align: 'left',
        field: 'party_name',
      },
      {
        name: 'date',
        label: 'Date',
        align: 'left',
        field: 'date',
        sortable: true,
      },
      { name: 'status', label: 'Status', align: 'center', field: 'status', sortable: true },
      {
        name: 'payment_mode',
        label: 'Payment Mode',
        align: 'left',
        field: 'payment_mode',
        sortable: false
      },
      {
        name: 'total_amount',
        label: 'Total amount',
        align: 'left',
        field: 'total_amount',
        sortable: true
      },
      {
        name: 'payment_receipts',
        label: 'Receipt(s)',
        align: 'left',
      },
      {
        name: 'receipt_amount',
        label: 'Receipt Amount',
        align: 'left',
      },
      {
        name: 'tds',
        label: 'TDS',
        align: 'left',
      },
      { name: 'actions', align: 'left', label: 'Actions' },
    ]

    const isImporting = ref(false)
    const fileToImport = ref(null)
    const showImportModal = ref(false)
    const importFileParseError = ref(null)
    const importFileRequiredColumns = [
      'Invoice Group ID',
      'Party',
      'Customer Name',
      'Address',
      'Due Date',
      'Discount Type',
      'Discount',
      'Trade Discount',
      'Payment Mode',
      'Remarks',
      'Is Export',
      'Sales Agent ID',
      'Status',
      'Row Item ID',
      'Row Quantity',
      'Row Rate',
      'Row Unit ID',
      'Row Discount Type',
      'Row Discount',
      'Row Tax Scheme ID',
      'Row Description',
    ]

    const $q = useQuasar()

    function validateImportFile(event) {
      importFileParseError.value = null
      const file = event.target.files[0]
      const reader = new FileReader()
      reader.onload = (e) => {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const sheetName = workbook.SheetNames[0]
        const sheet = workbook.Sheets[sheetName]
        const headers = XLSX.utils.sheet_to_json(sheet, { header: 1 })[0]
        for (let i = 0; i < importFileRequiredColumns.length; i++) {
          if (headers[i] !== importFileRequiredColumns[i]) {
            importFileParseError.value = `Invalid column at index ${i + 1}. found: ${headers[i]}, expected: ${importFileRequiredColumns[i]}`
            return
          }
        }
        fileToImport.value = file
      }
      reader.readAsArrayBuffer(file)
    }


    function openImportModal() {
      showImportModal.value = true
      fileToImport.value = null
    }

    function closeImportModal() {
      showImportModal.value = false
      fileToImport.value = null
    }

    function importInvoices() {
      if (isImporting.value || !fileToImport.value || importFileParseError.value) {
        return
      }
      isImporting.value = true
      const formData = new FormData()
      formData.append('file', fileToImport.value)
      useApi('v1/sales-voucher/import/', {
        method: 'POST',
        body: formData
      })
        .then(() => {
          $q.notify(
            {
              color: 'positive',
              message: 'Invoices import queued successfully!',
              icon: 'check_circle'
            }
          )
          showImportModal.value = false
        })
        .catch((error) => {
          if (error.data && error.data.error) {
            $q.notify(
              {
                color: 'negative',
                message: error.data.error,
                icon: 'error'
              }
            )
          } else {
            $q.notify(
              {
                color: 'negative',
                message: 'Error importing invoices',
                icon: 'error'
              }
            )
          }
        }).finally(() => {
          isImporting.value = false
        })
    }

    return {
      ...listData, newColumn, onDownloadXls, checkPermissions,
      openImportModal, closeImportModal, importInvoices, showImportModal, isImporting, fileToImport,
      validateImportFile, importFileParseError
    }

  }
}
</script>
