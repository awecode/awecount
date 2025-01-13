<script setup>
import * as XLSX from 'xlsx'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  helpText: {
    type: String,
    default: null,
  },
  sampleFileUrl: {
    type: String,
    default: null,
  },
  requiredColumns: {
    type: Array,
    required: true,
  },
  endpoint: {
    type: String,
    required: true,
  },
})
const showImportModal = defineModel('showImportModal')
const fileToImport = ref(null)
const importFileParseError = ref(null)
const isImporting = ref(false)

const $q = useQuasar()

watch(
  () => showImportModal.value,
  () => {
    fileToImport.value = null
  },
)

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
    body: formData,
  })
    .then(() => {
      $q.notify({
        color: 'positive',
        message: 'Import queued successfully!',
        icon: 'check_circle',
      })
      showImportModal.value = false
    })
    .catch((error) => {
      if (error.data && error.data.error) {
        $q.notify({
          color: 'negative',
          message: error.data.error,
          icon: 'error',
        })
      } else {
        $q.notify({
          color: 'negative',
          message: 'Something went wrong!',
          icon: 'error',
        })
      }
    })
    .finally(() => {
      isImporting.value = false
    })
}

function closeImportModal() {
  showImportModal.value = false
}
</script>

<template>
  <q-dialog v-model="showImportModal">
    <q-card class="overflow-visible" style="min-width: min(40vw, 500px)">
      <q-card-section class="bg-primary flex justify-between">
        <div class="text-h6 text-white">
          <span>{{ props.title }}</span>
        </div>
        <q-btn
          dense
          flat
          round
          class="text-primary bg-slate-200 opacity-95"
          icon="close"
          @click="closeImportModal"
        />
      </q-card-section>

      <q-card-section class="q-ma-md">
        <p class="text-caption">
          {{ props.helpText || 'Please select a file to import. The file should be in .xlsx format.' }}
          <a
            v-if="props.sampleFileUrl"
            download
            class="text-primary"
            :href="props.sampleFileUrl"
          >Download sample file</a>
        </p>
        <q-file
          v-model="fileToImport"
          dense
          flat
          accept=".xlsx"
          color="primary"
          label="Select file"
          :disable="isImporting"
          @input="validateImportFile"
        />
        <p v-if="importFileParseError" class="text-red-600">
          {{ importFileParseError }}
        </p>
        <div class="text-right q-mt-lg">
          <q-btn
            color="primary"
            label="Import"
            :disabled="isImporting || !fileToImport || importFileParseError"
            @click="importXLS()"
          />
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>
