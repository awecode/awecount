<template>
  <q-dialog v-model="showImportModal">
    <q-card style="min-width: min(40vw, 500px)" class="overflow-visible">
      <q-card-section class="bg-primary flex justify-between">
        <div class="text-h6 text-white">
          <span>{{ props.title }}</span>
        </div>
        <q-btn icon="close" class="text-primary bg-slate-200 opacity-95" flat round dense @click="closeImportModal" />
      </q-card-section>

      <q-card-section class="q-ma-md">
        <p class="text-caption">{{
          props.helpText || 'Please select a file to import. The file should be in .xlsx format.'
          }}
          <a v-if="props.sampleFileUrl" :href="props.sampleFileUrl" download class="text-primary">Download
            sample
            file</a>
        </p>
        <q-file @input="validateImportFile" v-model="fileToImport" accept=".xlsx" label="Select file" color="primary"
          flat dense :disable="isImporting">
        </q-file>
        <p v-if="importFileParseError" class="text-red-600">
          {{ importFileParseError }}
        </p>
        <div class="text-right q-mt-lg">
          <q-btn label="Import" color="primary" @click="importXLS()"
            :disabled="isImporting || !fileToImport || importFileParseError"></q-btn>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import * as XLSX from 'xlsx'

const showImportModal = defineModel('showImportModal');
const fileToImport = ref(null)
const importFileParseError = ref(null)
const isImporting = ref(false)

const $q = useQuasar()

watch(() => showImportModal.value, () => {
  fileToImport.value = null
})

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  helpText: {
    type: String,
    default: null
  },
  sampleFileUrl: {
    type: String,
    default: null
  },
  requiredColumns: {
    type: Array,
    required: true
  },
  endpoint: {
    type: String,
    required: true
  }
})
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
    for (let i = 0; i < props.requiredColumns.length; i++) {
      if (headers[i] !== props.requiredColumns[i]) {
        importFileParseError.value = `Invalid column at index ${i + 1}. found: ${headers[i]}, expected: ${props.requiredColumns[i]}`
        return
      }
    }
    fileToImport.value = file
  }
  reader.readAsArrayBuffer(file)
}


function importXLS() {
  if (isImporting.value || !fileToImport.value || importFileParseError.value) {
    return
  }
  isImporting.value = true
  const formData = new FormData()
  formData.append('file', fileToImport.value)
  useApi(props.endpoint, {
    method: 'POST',
    body: formData
  })
    .then(() => {
      $q.notify(
        {
          color: 'positive',
          message: 'Import queued successfully!',
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
            message: 'Something went wrong!',
            icon: 'error'
          }
        )
      }
    }).finally(() => {
      isImporting.value = false
    })
}

function closeImportModal() {
  showImportModal.value = false
}
</script>
