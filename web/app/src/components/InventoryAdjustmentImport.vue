<script setup>
const emit = defineEmits('modalClose', 'onImportSuccess')
const $q = useQuasar()
const file = ref(null)
const loading = ref(false)
const onSubmit = async () => {
  const formData = new FormData()
  formData.append('file', file.value)
  loading.value = true
  useApi('/v1/inventory-adjustment/import/', {
    method: 'POST',
    body: formData,
  })
    .then((response) => {
      loading.value = false
      $q.notify({
        color: 'green-6',
        message: 'Adjustment Imported!',
        icon: 'check_circle',
        position: 'top-right',
      })
      emit('modalClose')
      emit('onImportSuccess', response)
    })
    .catch((err) => {
      loading.value = false
      $q.notify({
        color: 'red-6',
        message: err.status !== '400' ? 'Server Error!' : `${err.message}`,
        icon: 'report_problem',
        position: 'top-right',
      })
    })
}
const onSampleDownload = async () => {
  const XLSX = await import('xlsx-js-style')
  const wb = XLSX.utils.book_new()
  const row = [
    { v: 'Item Code', s: { font: { bold: true } } },
    { v: 'Qty', s: { font: { bold: true } } },
    { v: 'Rate', s: { font: { bold: true } } },
    { v: 'Description', s: { font: { bold: true } } },
  ]
  const row2 = [{ v: 'Code' }, { v: 0 }, { v: 0 }, { v: 'Description' }, { v: 'Note: Remove the row and fill in your data. Please Do not remove any columns. if you don\'t want to insert data in any particular cell then leave it empty. Category column is optional. If the values of Can be Sold and Can be Purchased columns are t or T then it will be set to true, leaving the values to be something else or empty will result in those fields being false.' }]
  const ws = XLSX.utils.aoa_to_sheet([row, row2])
  XLSX.utils.book_append_sheet(wb, ws, 'Adjustment Voucher Import')
  XLSX.writeFile(wb, 'Adjustment_import_sample.xlsx')
}
</script>

<template>
  <div class="q-ma-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6">
          <span>Import Items From Excel Sheet</span>
        </div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="onSubmit()">
          <div class="row justify-end">
            <q-btn
              color="blue-5"
              icon="download"
              label="Download Sample"
              @click="onSampleDownload"
            />
          </div>
          <q-file
            v-model="file"
            accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel,text/comma-separated-values, text/csv, application/csv"
            label="Select File"
            name="file"
            style="max-width: 400px"
          />
          <q-btn
            class="q-mt-lg"
            color="green"
            type="submit"
            :disable="!file"
            :loading="loading"
          >
            Upload
          </q-btn>
        </q-form>
      </q-card-section>
    </q-card>
  </div>
</template>
