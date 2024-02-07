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
            <q-btn @click="onSampleDownload" color="blue-5" icon="download" label="Download Sample"></q-btn>
          </div>
          <q-file v-model="file" name="file" style="max-width: 400px;"
            accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel,text/comma-separated-values, text/csv, application/csv"
            label="Select File"></q-file>
          <div class="q-mt-md">
            <q-checkbox v-model="createNewCategory" label="Create New Category?"></q-checkbox> <q-icon color="grey-6"
              name="info" size="sm">
              <q-tooltip>
                Enabling this creates new category with the give name if it does not exist.
              </q-tooltip>
            </q-icon>
          </div>
          <div class="q-mt-md">
            <q-checkbox v-model="createNewUnit" label="Create New Unit?"></q-checkbox> <q-icon color="grey-6" name="info"
              size="sm">
              <q-tooltip>Enabling this creates new Unit with the give name if it does not exist.</q-tooltip>
            </q-icon>
          </div>
          <q-btn :loading="loading" :disable="!file" color="green" type="submit" class="q-mt-lg">Upload</q-btn>
        </q-form>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
const $q = useQuasar()
const file = ref(null)
const createNewCategory = ref(false)
const createNewUnit = ref(false)
const loading = ref(false)
const emit = defineEmits('modalClose', 'updateList')
const onSubmit = async () => {
  const formData = new FormData()
  formData.append('file', file.value)
  formData.append('create_new_category', createNewCategory.value)
  formData.append('create_new_unit', createNewUnit.value)
  loading.value = true
  useApi('/v1/items/import/', {
    method: 'POST',
    body: formData,
  })
    .then(() => {
      loading.value = false
      emit('updateList')
      $q.notify({
        color: 'green-6',
        message: 'Items Imported!',
        icon: 'check_circle',
        position: 'top-right',
      })
    })
    .catch((err) => {
      loading.value = false
      $q.notify({
        color: 'red-6',
        message:
          err.status !== '400'
            ? 'Server Error! Please contact us with the problem.'
            : `${err.message}`,
        icon: 'report_problem',
        position: 'top-right',
      })
    })
}
const onSampleDownload = async () => {
  const XLSX = await import('xlsx-js-style')
  const wb = XLSX.utils.book_new()
  const row = [
    { v: 'Name', s: { font: { bold: true } } },
    { v: 'Code', s: { font: { bold: true } } },
    { v: 'Category', s: { font: { bold: true } } },
    { v: 'Cost Price', s: { font: { bold: true } } },
    { v: 'Selling Price', s: { font: { bold: true } } },
    { v: 'Can be Purchased', s: { font: { bold: true } } },
    { v: 'Can be Sold', s: { font: { bold: true } } },
    { v: 'Track Inventory', s: { font: { bold: true } } },
    { v: 'Tax Scheme', s: { font: { bold: true } } },
    { v: 'Unit', s: { font: { bold: true } } },
  ];
  const row2 = [
    { v: 'Test Item', },
    { v: 'Code', },
    { v: 'Category_name', },
    { v: '0', },
    { v: '0', },
    { v: 't', },
    { v: 'T', },
    { v: 't', },
    { v: 'Tax_name', },
    { v: 'Unit_name', },
    { v: 'Note: Remove the row and fill in your data. Please Do not remove any columns. if you don\'t want to insert data in any particular cell then leave it empty. Category column is optional. If the values of Can be Sold and Can be Purchased columns are t or T then it will be set to true, leaving the values to be something else or empty will result in those fields being false.' }
  ]
  const ws = XLSX.utils.aoa_to_sheet([row, row2])
  XLSX.utils.book_append_sheet(wb, ws, 'Items Import')
  XLSX.writeFile(wb, 'Items_import_sample.xlsx')
}
</script>
