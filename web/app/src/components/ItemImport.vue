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
                        accept=".xml,,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        label="Select File"></q-file>
                    <div class="q-mt-md">
                        <q-checkbox v-model="createNewCategory" label="Create New Category?"></q-checkbox> <q-icon
                            color="grey-6" name="info" size="sm"
                            title="Enabling this creates new category if the given category does not exist."></q-icon>
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
const loading = ref(false)
const emit = defineEmits('modalClose')
const onSubmit = async () => {
    const formData = new FormData()
    formData.append('file', file.value)
    formData.append('create_new_category', createNewCategory.value)
    loading.value = true
    useApi('/v1/items/import/', {
        method: 'POST',
        body: formData,
    })
        .then(() => {
            loading.value = false
            emit('modalClose')
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
    const XLSX = await import("xlsx-js-style")
    const wb = XLSX.utils.book_new()
    const row = [
        { v: "Name", s: { font: { bold: true } } },
        { v: "Code", s: { font: { bold: true } } },
        { v: "Category", s: { font: { bold: true } } },
        { v: "Cost Price", s: { font: { bold: true } } },
        { v: "Selling Price", s: { font: { bold: true } } },
        { v: "Can be Purchased", s: { font: { bold: true } } },
        { v: "Can be Sold", s: { font: { bold: true } } },
    ];
    const row2 = [
        { v: "Test Item", },
        { v: "Code", },
        { v: "Category_name", },
        { v: "0", },
        { v: "0", },
        { v: "t", },
        { v: "T", },
        {v: 'Note: Remove the row and fill in your data. Please Do not remove any columns. if you don\'t to insert data in any particular cell then leave it empty.'}
    ]
    const ws = XLSX.utils.aoa_to_sheet([row, row2])
    XLSX.utils.book_append_sheet(wb, ws, "Items Import")
    XLSX.writeFile(wb, "Items_import_sample.xlsx")
} 
</script>
